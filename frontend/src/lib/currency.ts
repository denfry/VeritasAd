/**
 * Currency data with flags, symbols, and codes
 * Source: Frankfurter API + emoji flags
 */

export interface Currency {
  code: string
  name: string
  symbol: string
  flag: string
  nativeSymbol?: string
}

/**
 * Popular currencies for quick access
 */
export const POPULAR_CURRENCIES: Currency[] = [
  { code: 'RUB', name: 'Russian Ruble', symbol: '₽', flag: '🇷🇺', nativeSymbol: 'руб.' },
  { code: 'USD', name: 'US Dollar', symbol: '$', flag: '🇺🇸' },
  { code: 'EUR', name: 'Euro', symbol: '€', flag: '🇪🇺' },
  { code: 'GBP', name: 'British Pound', symbol: '£', flag: '🇬🇧' },
  { code: 'CNY', name: 'Chinese Yuan', symbol: '¥', flag: '🇨🇳' },
  { code: 'JPY', name: 'Japanese Yen', symbol: '¥', flag: '🇯🇵' },
  { code: 'KRW', name: 'South Korean Won', symbol: '₩', flag: '🇰🇷' },
  { code: 'KZT', name: 'Kazakhstani Tenge', symbol: '₸', flag: '🇰🇿' },
  { code: 'BYN', name: 'Belarusian Ruble', symbol: 'Br', flag: '🇧🇾' },
  { code: 'UAH', name: 'Ukrainian Hryvnia', symbol: '₴', flag: '🇺🇦' },
  { code: 'TRY', name: 'Turkish Lira', symbol: '₺', flag: '🇹🇷' },
  { code: 'INR', name: 'Indian Rupee', symbol: '₹', flag: '🇮🇳' },
]

/**
 * All supported currencies (150+ countries)
 */
export const ALL_CURRENCIES: Currency[] = [
  ...POPULAR_CURRENCIES,
  { code: 'AED', name: 'UAE Dirham', symbol: 'AED', flag: '🇦🇪', nativeSymbol: 'د.إ' },
  { code: 'AFN', name: 'Afghan Afghani', symbol: 'Af', flag: '🇦🇫', nativeSymbol: '؋' },
  { code: 'ALL', name: 'Albanian Lek', symbol: 'ALL', flag: '🇦🇱', nativeSymbol: 'Lek' },
  { code: 'AMD', name: 'Armenian Dram', symbol: 'AMD', flag: '🇦🇲', nativeSymbol: 'դր.' },
  { code: 'ANG', name: 'Netherlands Antillean Guilder', symbol: 'ƒ', flag: '🇨🇼' },
  { code: 'AOA', name: 'Angolan Kwanza', symbol: 'Kz', flag: '🇦🇴' },
  { code: 'ARS', name: 'Argentine Peso', symbol: 'AR$', flag: '🇦🇷', nativeSymbol: '$' },
  { code: 'AUD', name: 'Australian Dollar', symbol: 'A$', flag: '🇦🇺', nativeSymbol: '$' },
  { code: 'AWG', name: 'Aruban Florin', symbol: 'Afl', flag: '🇦🇼' },
  { code: 'AZN', name: 'Azerbaijani Manat', symbol: 'man.', flag: '🇦🇿', nativeSymbol: 'ман.' },
  { code: 'BAM', name: 'Bosnia-Herzegovina Convertible Mark', symbol: 'KM', flag: '🇧🇦' },
  { code: 'BBD', name: 'Barbadian Dollar', symbol: 'BBD$', flag: '🇧🇧', nativeSymbol: '$' },
  { code: 'BDT', name: 'Bangladeshi Taka', symbol: 'Tk', flag: '🇧🇩', nativeSymbol: '৳' },
  { code: 'BGN', name: 'Bulgarian Lev', symbol: 'BGN', flag: '🇧🇬', nativeSymbol: 'лв.' },
  { code: 'BHD', name: 'Bahraini Dinar', symbol: 'BD', flag: '🇧🇭', nativeSymbol: 'د.ب' },
  { code: 'BIF', name: 'Burundian Franc', symbol: 'FBu', flag: '🇧🇮' },
  { code: 'BMD', name: 'Bermudian Dollar', symbol: '$', flag: '🇧🇲' },
  { code: 'BND', name: 'Brunei Dollar', symbol: 'BN$', flag: '🇧🇳', nativeSymbol: '$' },
  { code: 'BOB', name: 'Bolivian Boliviano', symbol: 'Bs', flag: '🇧🇴' },
  { code: 'BRL', name: 'Brazilian Real', symbol: 'R$', flag: '🇧🇷' },
  { code: 'BSD', name: 'Bahamian Dollar', symbol: 'B$', flag: '🇧🇸', nativeSymbol: '$' },
  { code: 'BTN', name: 'Bhutanese Ngultrum', symbol: 'Nu.', flag: '🇧🇹' },
  { code: 'BWP', name: 'Botswanan Pula', symbol: 'BWP', flag: '🇧🇼', nativeSymbol: 'P' },
  { code: 'BZD', name: 'Belize Dollar', symbol: 'BZ$', flag: '🇧🇿', nativeSymbol: '$' },
  { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$', flag: '🇨🇦', nativeSymbol: '$' },
  { code: 'CDF', name: 'Congolese Franc', symbol: 'CDF', flag: '🇨🇩', nativeSymbol: 'FrCD' },
  { code: 'CHF', name: 'Swiss Franc', symbol: 'CHF', flag: '🇨🇭' },
  { code: 'CLP', name: 'Chilean Peso', symbol: 'CL$', flag: '🇨🇱', nativeSymbol: '$' },
  { code: 'COP', name: 'Colombian Peso', symbol: 'CO$', flag: '🇨🇴', nativeSymbol: '$' },
  { code: 'CRC', name: 'Costa Rican Colón', symbol: '₡', flag: '🇨🇷' },
  { code: 'CUP', name: 'Cuban Peso', symbol: '$MN', flag: '🇨🇺', nativeSymbol: '$' },
  { code: 'CVE', name: 'Cape Verdean Escudo', symbol: 'CV$', flag: '🇨🇻' },
  { code: 'CZK', name: 'Czech Koruna', symbol: 'Kč', flag: '🇨🇿' },
  { code: 'DJF', name: 'Djiboutian Franc', symbol: 'Fdj', flag: '🇩🇯' },
  { code: 'DKK', name: 'Danish Krone', symbol: 'kr', flag: '🇩🇰', nativeSymbol: 'Dkr' },
  { code: 'DOP', name: 'Dominican Peso', symbol: 'RD$', flag: '🇩🇴' },
  { code: 'DZD', name: 'Algerian Dinar', symbol: 'DA', flag: '🇩🇿', nativeSymbol: 'د.ج' },
  { code: 'EGP', name: 'Egyptian Pound', symbol: 'EGP', flag: '🇪🇬', nativeSymbol: 'ج.م' },
  { code: 'ERN', name: 'Eritrean Nakfa', symbol: 'Nfk', flag: '🇪🇷' },
  { code: 'ETB', name: 'Ethiopian Birr', symbol: 'Br', flag: '🇪🇹' },
  { code: 'FJD', name: 'Fijian Dollar', symbol: 'FJ$', flag: '🇫🇯', nativeSymbol: '$' },
  { code: 'FKP', name: 'Falkland Islands Pound', symbol: '£', flag: '🇫🇰' },
  { code: 'FOK', name: 'Faroese Króna', symbol: 'kr', flag: '🇫🇴' },
  { code: 'GEL', name: 'Georgian Lari', symbol: 'GEL', flag: '🇬🇪' },
  { code: 'GGP', name: 'Guernsey Pound', symbol: '£', flag: '🇬🇬' },
  { code: 'GHS', name: 'Ghanaian Cedi', symbol: 'GH₵', flag: '🇬🇭' },
  { code: 'GIP', name: 'Gibraltar Pound', symbol: '£', flag: '🇬🇮' },
  { code: 'GMD', name: 'Gambian Dalasi', symbol: 'D', flag: '🇬🇲' },
  { code: 'GNF', name: 'Guinean Franc', symbol: 'FG', flag: '🇬🇳' },
  { code: 'GTQ', name: 'Guatemalan Quetzal', symbol: 'GTQ', flag: '🇬🇹', nativeSymbol: 'Q' },
  { code: 'GYD', name: 'Guyanese Dollar', symbol: 'G$', flag: '🇬🇾', nativeSymbol: '$' },
  { code: 'HKD', name: 'Hong Kong Dollar', symbol: 'HK$', flag: '🇭🇰', nativeSymbol: '$' },
  { code: 'HNL', name: 'Honduran Lempira', symbol: 'HNL', flag: '🇭🇳', nativeSymbol: 'L' },
  { code: 'HRK', name: 'Croatian Kuna', symbol: 'kn', flag: '🇭🇷' },
  { code: 'HTG', name: 'Haitian Gourde', symbol: 'G', flag: '🇭🇹' },
  { code: 'HUF', name: 'Hungarian Forint', symbol: 'Ft', flag: '🇭🇺' },
  { code: 'IDR', name: 'Indonesian Rupiah', symbol: 'Rp', flag: '🇮🇩' },
  { code: 'ILS', name: 'Israeli New Sheqel', symbol: '₪', flag: '🇮🇱' },
  { code: 'IMP', name: 'Manx Pound', symbol: '£', flag: '🇮🇲' },
  { code: 'IQD', name: 'Iraqi Dinar', symbol: 'IQD', flag: '🇮🇶', nativeSymbol: 'د.ع' },
  { code: 'IRR', name: 'Iranian Rial', symbol: 'IRR', flag: '🇮🇷', nativeSymbol: '﷼' },
  { code: 'ISK', name: 'Icelandic Króna', symbol: 'kr', flag: '🇮🇸', nativeSymbol: 'Ikr' },
  { code: 'JEP', name: 'Jersey Pound', symbol: '£', flag: '🇯🇪' },
  { code: 'JMD', name: 'Jamaican Dollar', symbol: 'J$', flag: '🇯🇲', nativeSymbol: '$' },
  { code: 'JOD', name: 'Jordanian Dinar', symbol: 'JD', flag: '🇯🇴', nativeSymbol: 'د.أ' },
  { code: 'KES', name: 'Kenyan Shilling', symbol: 'Ksh', flag: '🇰🇪' },
  { code: 'KGS', name: 'Kyrgyzstani Som', symbol: 'с', flag: '🇰🇬' },
  { code: 'KHR', name: 'Cambodian Riel', symbol: 'KHR', flag: '🇰🇭', nativeSymbol: '៛' },
  { code: 'KID', name: 'Kiribati Dollar', symbol: '$', flag: '🇰🇮' },
  { code: 'KMF', name: 'Comorian Franc', symbol: 'CF', flag: '🇰🇲', nativeSymbol: 'FC' },
  { code: 'KWD', name: 'Kuwaiti Dinar', symbol: 'KD', flag: '🇰🇼', nativeSymbol: 'د.ك' },
  { code: 'KYD', name: 'Cayman Islands Dollar', symbol: '$', flag: '🇰🇾' },
  { code: 'LAK', name: 'Lao Kip', symbol: '₭', flag: '🇱🇦' },
  { code: 'LBP', name: 'Lebanese Pound', symbol: 'LB£', flag: '🇱🇧', nativeSymbol: 'ل.ل' },
  { code: 'LKR', name: 'Sri Lankan Rupee', symbol: 'SLRs', flag: '🇱🇰', nativeSymbol: 'SL Re' },
  { code: 'LRD', name: 'Liberian Dollar', symbol: '$', flag: '🇱🇷' },
  { code: 'LSL', name: 'Lesotho Loti', symbol: 'L', flag: '🇱🇸' },
  { code: 'LYD', name: 'Libyan Dinar', symbol: 'LD', flag: '🇱🇾', nativeSymbol: 'د.ل' },
  { code: 'MAD', name: 'Moroccan Dirham', symbol: 'MAD', flag: '🇲🇦', nativeSymbol: 'د.م' },
  { code: 'MDL', name: 'Moldovan Leu', symbol: 'MDL', flag: '🇲🇩' },
  { code: 'MGA', name: 'Malagasy Ariary', symbol: 'MGA', flag: '🇲🇬' },
  { code: 'MKD', name: 'Macedonian Denar', symbol: 'MKD', flag: '🇲🇰' },
  { code: 'MMK', name: 'Myanmar Kyat', symbol: 'MMK', flag: '🇲🇲', nativeSymbol: 'K' },
  { code: 'MNT', name: 'Mongolian Tugrik', symbol: '₮', flag: '🇲🇳' },
  { code: 'MOP', name: 'Macanese Pataca', symbol: 'MOP$', flag: '🇲🇴' },
  { code: 'MRU', name: 'Mauritanian Ouguiya', symbol: 'UM', flag: '🇲🇷', nativeSymbol: 'أوقية' },
  { code: 'MUR', name: 'Mauritian Rupee', symbol: 'MURs', flag: '🇲🇺' },
  { code: 'MVR', name: 'Maldivian Rufiyaa', symbol: 'MVR', flag: '🇲🇻', nativeSymbol: 'ރ' },
  { code: 'MWK', name: 'Malawian Kwacha', symbol: 'MK', flag: '🇲🇼' },
  { code: 'MXN', name: 'Mexican Peso', symbol: 'MX$', flag: '🇲🇽', nativeSymbol: '$' },
  { code: 'MYR', name: 'Malaysian Ringgit', symbol: 'RM', flag: '🇲🇾' },
  { code: 'MZN', name: 'Mozambican Metical', symbol: 'MTn', flag: '🇲🇿' },
  { code: 'NAD', name: 'Namibian Dollar', symbol: 'N$', flag: '🇳🇦' },
  { code: 'NGN', name: 'Nigerian Naira', symbol: '₦', flag: '🇳🇬' },
  { code: 'NIO', name: 'Nicaraguan Córdoba', symbol: 'C$', flag: '🇳🇮' },
  { code: 'NOK', name: 'Norwegian Krone', symbol: 'kr', flag: '🇳🇴', nativeSymbol: 'Nkr' },
  { code: 'NPR', name: 'Nepalese Rupee', symbol: 'NPRs', flag: '🇳🇵', nativeSymbol: 'नेरू' },
  { code: 'NZD', name: 'New Zealand Dollar', symbol: 'NZ$', flag: '🇳🇿', nativeSymbol: '$' },
  { code: 'OMR', name: 'Omani Rial', symbol: 'OMR', flag: '🇴🇲', nativeSymbol: 'ر.ع' },
  { code: 'PAB', name: 'Panamanian Balboa', symbol: 'B/.', flag: '🇵🇦' },
  { code: 'PEN', name: 'Peruvian Nuevo Sol', symbol: 'S/.', flag: '🇵🇪' },
  { code: 'PGK', name: 'Papua New Guinean Kina', symbol: 'K', flag: '🇵🇬' },
  { code: 'PHP', name: 'Philippine Peso', symbol: '₱', flag: '🇵🇭' },
  { code: 'PKR', name: 'Pakistani Rupee', symbol: 'PKRs', flag: '🇵🇰', nativeSymbol: '₨' },
  { code: 'PLN', name: 'Polish Zloty', symbol: 'zł', flag: '🇵🇱' },
  { code: 'PYG', name: 'Paraguayan Guarani', symbol: '₲', flag: '🇵🇾' },
  { code: 'QAR', name: 'Qatari Rial', symbol: 'QR', flag: '🇶🇦', nativeSymbol: 'ر.ق' },
  { code: 'RON', name: 'Romanian Leu', symbol: 'RON', flag: '🇷🇴' },
  { code: 'RSD', name: 'Serbian Dinar', symbol: 'din.', flag: '🇷🇸', nativeSymbol: 'дин.' },
  { code: 'RWF', name: 'Rwandan Franc', symbol: 'RWF', flag: '🇷🇼', nativeSymbol: 'FR' },
  { code: 'SAR', name: 'Saudi Riyal', symbol: 'SR', flag: '🇸🇦', nativeSymbol: 'ر.س' },
  { code: 'SBD', name: 'Solomon Islands Dollar', symbol: '$', flag: '🇸🇧', nativeSymbol: 'SI$' },
  { code: 'SCR', name: 'Seychellois Rupee', symbol: '₨', flag: '🇸🇨' },
  { code: 'SDG', name: 'Sudanese Pound', symbol: 'SDG', flag: '🇸🇩' },
  { code: 'SEK', name: 'Swedish Krona', symbol: 'kr', flag: '🇸🇪', nativeSymbol: 'Skr' },
  { code: 'SGD', name: 'Singapore Dollar', symbol: 'S$', flag: '🇸🇬', nativeSymbol: '$' },
  { code: 'SHP', name: 'Saint Helenian Pound', symbol: '£', flag: '🇸🇭' },
  { code: 'SLE', name: 'Sierra Leonean Leone', symbol: 'Le', flag: '🇸🇱' },
  { code: 'SOS', name: 'Somali Shilling', symbol: 'Ssh', flag: '🇸🇴' },
  { code: 'SRD', name: 'Surinamese Dollar', symbol: 'Sr$', flag: '🇸🇷', nativeSymbol: '$' },
  { code: 'SSP', name: 'South Sudanese Pound', symbol: '£', flag: '🇸🇸' },
  { code: 'STN', name: 'São Tomé and Príncipe Dobra', symbol: 'Db', flag: '🇸🇹' },
  { code: 'SYP', name: 'Syrian Pound', symbol: 'SY£', flag: '🇸🇾', nativeSymbol: 'ل.س' },
  { code: 'SZL', name: 'Swazi Lilangeni', symbol: 'L', flag: '🇸🇿' },
  { code: 'THB', name: 'Thai Baht', symbol: '฿', flag: '🇹🇭' },
  { code: 'TJS', name: 'Tajikistani Somoni', symbol: 'ЅМ', flag: '🇹🇯' },
  { code: 'TMT', name: 'Turkmenistani Manat', symbol: 'm', flag: '🇹🇲' },
  { code: 'TND', name: 'Tunisian Dinar', symbol: 'DT', flag: '🇹🇳', nativeSymbol: 'د.ت' },
  { code: 'TOP', name: 'Tongan Paʻanga', symbol: 'T$', flag: '🇹🇴' },
  { code: 'TTD', name: 'Trinidad and Tobago Dollar', symbol: 'TT$', flag: '🇹🇹', nativeSymbol: '$' },
  { code: 'TVD', name: 'Tuvaluan Dollar', symbol: '$', flag: '🇹🇻' },
  { code: 'TWD', name: 'New Taiwan Dollar', symbol: 'NT$', flag: '🇹🇼' },
  { code: 'TZS', name: 'Tanzanian Shilling', symbol: 'TSh', flag: '🇹🇿' },
  { code: 'UZS', name: 'Uzbekistan Som', symbol: 'UZS', flag: '🇺🇿' },
  { code: 'VES', name: 'Venezuelan Bolívar', symbol: 'Bs.F', flag: '🇻🇪' },
  { code: 'VND', name: 'Vietnamese Dong', symbol: '₫', flag: '🇻🇳' },
  { code: 'VUV', name: 'Vanuatu Vatu', symbol: 'Vt', flag: '🇻🇺' },
  { code: 'WST', name: 'Samoan Tala', symbol: 'WS$', flag: '🇼🇸', nativeSymbol: '$' },
  { code: 'XAF', name: 'CFA Franc BEAC', symbol: 'FCFA', flag: '🇨🇫' },
  { code: 'XCD', name: 'East Caribbean Dollar', symbol: '$', flag: '🇦🇬' },
  { code: 'XDR', name: 'IMF Special Drawing Rights', symbol: 'SDR', flag: '🏴' },
  { code: 'XOF', name: 'CFA Franc BCEAO', symbol: 'CFA', flag: '🇨🇮' },
  { code: 'XPF', name: 'CFP Franc', symbol: 'Fr', flag: '🇵🇫' },
  { code: 'YER', name: 'Yemeni Rial', symbol: 'YR', flag: '🇾🇪', nativeSymbol: 'ر.ي' },
  { code: 'ZAR', name: 'South African Rand', symbol: 'R', flag: '🇿🇦' },
  { code: 'ZMW', name: 'Zambian Kwacha', symbol: 'ZK', flag: '🇿🇲' },
  { code: 'ZWL', name: 'Zimbabwean Dollar', symbol: 'Z$', flag: '🇿🇼', nativeSymbol: '$' },
]

/**
 * Get flag SVG URL from CDN (Flagpack or CountryFlagsAPI)
 * This ensures consistent rendering across all OS (Windows often lacks flag emojis)
 */
export function getFlagUrl(code: string): string {
  // Mapping some currency codes to country codes for the flag API
  const mapping: Record<string, string> = {
    'USD': 'us', 'EUR': 'eu', 'GBP': 'gb', 'CNY': 'cn', 'JPY': 'jp',
    'RUB': 'ru', 'KRW': 'kr', 'KZT': 'kz', 'BYN': 'by', 'UAH': 'ua',
    'TRY': 'tr', 'INR': 'in', 'AED': 'ae', 'CAD': 'ca', 'AUD': 'au',
    'CHF': 'ch', 'PLN': 'pl', 'SEK': 'se', 'NOK': 'no', 'DKK': 'dk'
  }
  
  const countryCode = mapping[code] || code.substring(0, 2).toLowerCase()
  // Use Flagpack or similar reliable CDN
  return `https://purecatamphetamine.github.io/country-flag-icons/3x2/${countryCode.toUpperCase()}.svg`
}

/**
 * Get currency by code
 */
export function getCurrencyByCode(code: string): Currency | undefined {
  return ALL_CURRENCIES.find(c => c.code === code)
}

/**
 * Format price with currency symbol
 */
export function formatPrice(amount: number, currencyCode: string): string {
  const currency = getCurrencyByCode(currencyCode)
  if (!currency) return `${amount} ${currencyCode}`

  // Special formatting for some currencies
  const symbol = currency.symbol || currencyCode
  const formatted = amount.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })

  // Some symbols go before, some after
  const symbolsBefore = ['$', '€', '£', '¥', '₹', '₽', '₺', '₴', '₸', 'Br', '₩', '₪', '₱', '₫']
  if (symbolsBefore.includes(symbol)) {
    return `${symbol}${formatted}`
  }
  
  return `${formatted} ${symbol}`
}

/**
 * Base currency for the application (prices are stored in RUB)
 */
export const BASE_CURRENCY = 'RUB'
