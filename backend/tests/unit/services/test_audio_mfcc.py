"""Tests for MFCC + KNN audio analysis (thesis sec. 3.2)."""
import numpy as np
import pytest

pytest.importorskip("librosa")
sf = pytest.importorskip("soundfile")


def _make_analyzer():
    # Avoid loading Whisper by patching ModelManager via a lightweight subclass.
    from app.services.audio_analyzer import AudioAnalyzer

    analyzer = AudioAnalyzer.__new__(AudioAnalyzer)
    analyzer.model = None
    analyzer._knn_model = None
    analyzer._knn_loaded = True  # pretend "no model on disk"
    return analyzer


def test_extract_mfcc_windows_shape(tmp_path):
    sr = 16000
    # 6 seconds of noise -> at 2s window / 1s hop -> ~5 windows.
    y = np.random.randn(sr * 6).astype(np.float32)
    wav = tmp_path / "noise.wav"
    sf.write(str(wav), y, sr)

    analyzer = _make_analyzer()
    feats = analyzer.extract_mfcc_windows(wav)
    assert feats.ndim == 2
    assert feats.shape[1] == 40  # n_mfcc
    assert feats.shape[0] >= 4


def test_detect_ad_acoustics_without_model(tmp_path):
    analyzer = _make_analyzer()
    # No trained KNN model -> not available, score 0.
    result = analyzer.detect_ad_acoustics(tmp_path / "missing.wav")
    assert result["available"] is False
    assert result["score"] == 0.0
