from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.ml.ad_dataset import AD_CLASSES, NormalizedAdRecord


TOKEN_RE = re.compile(r"[\w#@./:-]+", re.UNICODE)
MODEL_FORMAT_VERSION = 1


@dataclass(frozen=True)
class AdModelPrediction:
    predicted_class: str
    class_probabilities: dict[str, float]
    model_version: str

    @property
    def confidence(self) -> float:
        return max(self.class_probabilities.values(), default=0.0)

    @property
    def has_advertising(self) -> bool:
        return self.predicted_class in {"official", "unofficial", "hidden_ad"}


def tokenize(text: str) -> list[str]:
    return [token.casefold() for token in TOKEN_RE.findall(text or "") if len(token) >= 2]


def _softmax(logits: dict[str, float]) -> dict[str, float]:
    if not logits:
        return {}
    max_logit = max(logits.values())
    exps = {label: math.exp(value - max_logit) for label, value in logits.items()}
    total = sum(exps.values()) or 1.0
    return {label: value / total for label, value in exps.items()}


class HybridAdClassifier:
    """Small serializable text + numeric-feature classifier.

    This intentionally avoids new runtime dependencies so the first production
    ML foundation can be trained and loaded in the current backend environment.
    """

    def __init__(
        self,
        *,
        version: str,
        classes: list[str],
        priors: dict[str, float],
        token_counts: dict[str, dict[str, int]],
        token_totals: dict[str, int],
        vocabulary: list[str],
        feature_means: dict[str, dict[str, float]],
    ) -> None:
        self.version = version
        self.classes = classes
        self.priors = priors
        self.token_counts = token_counts
        self.token_totals = token_totals
        self.vocabulary = vocabulary
        self.feature_means = feature_means

    def predict(self, record: NormalizedAdRecord) -> AdModelPrediction:
        tokens = tokenize(record.text)
        vocabulary_size = max(len(self.vocabulary), 1)
        logits: dict[str, float] = {}

        for label in self.classes:
            logit = math.log(max(self.priors.get(label, 0.0), 1e-9))
            counts = self.token_counts.get(label, {})
            total = self.token_totals.get(label, 0)
            denominator = total + vocabulary_size
            for token in tokens:
                logit += math.log((counts.get(token, 0) + 1) / denominator)

            means = self.feature_means.get(label, {})
            for feature_name, value in record.features.items():
                if feature_name not in means:
                    continue
                logit -= abs(value - means[feature_name]) * 0.35
            logits[label] = logit

        probabilities = _softmax(logits)
        predicted_class = max(probabilities, key=probabilities.get)
        return AdModelPrediction(
            predicted_class=predicted_class,
            class_probabilities=probabilities,
            model_version=self.version,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_version": MODEL_FORMAT_VERSION,
            "version": self.version,
            "classes": self.classes,
            "priors": self.priors,
            "token_counts": self.token_counts,
            "token_totals": self.token_totals,
            "vocabulary": self.vocabulary,
            "feature_means": self.feature_means,
        }

    def save(self, path: str | Path) -> None:
        artifact_path = Path(path)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "HybridAdClassifier":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("format_version") != MODEL_FORMAT_VERSION:
            raise ValueError("unsupported ad model artifact format")
        return cls(
            version=data["version"],
            classes=list(data["classes"]),
            priors={str(k): float(v) for k, v in data["priors"].items()},
            token_counts={
                str(label): {str(token): int(count) for token, count in counts.items()}
                for label, counts in data["token_counts"].items()
            },
            token_totals={str(k): int(v) for k, v in data["token_totals"].items()},
            vocabulary=list(data["vocabulary"]),
            feature_means={
                str(label): {str(name): float(value) for name, value in features.items()}
                for label, features in data["feature_means"].items()
            },
        )


def train_classifier(records: list[NormalizedAdRecord], *, version: str) -> HybridAdClassifier:
    if not records:
        raise ValueError("cannot train ad classifier without records")

    classes = [label for label in AD_CLASSES if any(record.label == label for record in records)]
    class_counts = Counter(record.label for record in records)
    token_counts: dict[str, Counter[str]] = defaultdict(Counter)
    feature_sums: dict[str, Counter[str]] = defaultdict(Counter)
    vocabulary: set[str] = set()

    for record in records:
        tokens = tokenize(record.text)
        token_counts[record.label].update(tokens)
        vocabulary.update(tokens)
        feature_sums[record.label].update(record.features)

    total_records = len(records)
    priors = {
        label: (class_counts[label] + 1) / (total_records + len(classes))
        for label in classes
    }
    token_totals = {label: sum(token_counts[label].values()) for label in classes}
    feature_means = {
        label: {
            feature_name: value / class_counts[label]
            for feature_name, value in feature_sums[label].items()
        }
        for label in classes
    }

    return HybridAdClassifier(
        version=version,
        classes=classes,
        priors=priors,
        token_counts={label: dict(token_counts[label]) for label in classes},
        token_totals=token_totals,
        vocabulary=sorted(vocabulary),
        feature_means=feature_means,
    )


def evaluate_records(
    model: HybridAdClassifier,
    records: list[NormalizedAdRecord],
) -> dict[str, Any]:
    confusion: dict[str, Counter[str]] = {label: Counter() for label in model.classes}
    correct = 0
    for record in records:
        prediction = model.predict(record)
        confusion.setdefault(record.label, Counter())[prediction.predicted_class] += 1
        if prediction.predicted_class == record.label:
            correct += 1

    per_class: dict[str, dict[str, float]] = {}
    for label in model.classes:
        true_positive = confusion.get(label, Counter()).get(label, 0)
        predicted_positive = sum(row.get(label, 0) for row in confusion.values())
        actual_positive = sum(confusion.get(label, Counter()).values())
        precision = true_positive / predicted_positive if predicted_positive else 0.0
        recall = true_positive / actual_positive if actual_positive else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": float(actual_positive),
        }

    return {
        "total": len(records),
        "accuracy": correct / len(records) if records else 0.0,
        "per_class": per_class,
    }
