"""
Sensitive Information Detector

This module provides functionality to detect various types of sensitive information
in text using regular expressions.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Pattern, Tuple


@dataclass
class SensitiveMatch:
    """Represents a match of sensitive information."""

    start: int
    end: int
    text: str
    pattern_name: str
    confidence: float = 1.0


class SensitiveDetector:
    """Detector for various types of sensitive information."""

    def __init__(self):
        """Initialize the detector with predefined patterns."""
        self.patterns: Dict[str, Pattern] = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, Pattern]:
        """Compile all sensitive information patterns."""
        patterns = {
            # Email addresses
            "email": re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.IGNORECASE
            ),
            # Phone numbers (various formats)
            "phone": re.compile(
                r"(?:\+\d{1,3}[-.\s]?)?\(?(?:\d{2,4})\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
                re.IGNORECASE,
            ),
            # Credit card numbers
            "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b", re.IGNORECASE),
            # Social Security Numbers (US format)
            "ssn": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b", re.IGNORECASE),
            # Japanese personal numbers (My Number)
            "jp_mynumber": re.compile(
                r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", re.IGNORECASE
            ),
            # IP addresses (IPv4)
            "ipv4": re.compile(
                r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
                re.IGNORECASE,
            ),
            # IPv6 addresses
            "ipv6": re.compile(
                r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b", re.IGNORECASE
            ),
            # API keys (various formats)
            "api_key": re.compile(
                r'\b(?:api[_-]?key|apikey|access[_-]?token|secret[_-]?key|key)["\']?\s*[:=]\s*["\']?([A-Za-z0-9+/=_-]{8,})["\']?',
                re.IGNORECASE,
            ),
            # AWS Access Keys
            "aws_access_key": re.compile(r"\b(AKIA[0-9A-Z]{16})\b", re.IGNORECASE),
            # AWS Secret Keys
            "aws_secret_key": re.compile(r"\b[A-Za-z0-9+/]{40}\b", re.IGNORECASE),
            # GitHub tokens
            "github_token": re.compile(
                r"\b(?:ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9_]{36}\b", re.IGNORECASE
            ),
            # JWT tokens
            "jwt_token": re.compile(
                r"\b[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", re.IGNORECASE
            ),
            # Passwords (basic pattern)
            "password": re.compile(
                r'\b(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s"\']{6,})["\']?',
                re.IGNORECASE,
            ),
            # Database connection strings
            "db_connection": re.compile(
                r"(?:mongodb|mysql|postgresql|sqlite|oracle)://[^\s]+", re.IGNORECASE
            ),
            # URLs with credentials
            "url_with_credentials": re.compile(
                r"https?://[^\s:]+:[^\s@]+@[^\s]+", re.IGNORECASE
            ),
            # Private keys
            "private_key": re.compile(
                r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
                re.IGNORECASE,
            ),
            # Japanese personal names (surname + given name) - more restrictive
            "jp_person_name": re.compile(
                r"\b[一-龯々]{2,4}[\s　]+[一-龯々ひらがなカタカナ]{2,4}\b|名前[:：]\s*[一-龯々ひらがなカタカナ]{2,8}|氏名[:：]\s*[一-龯々ひらがなカタカナ]{2,8}|担当者[:：]\s*[一-龯々ひらがなカタカナ]{2,8}",
                re.IGNORECASE,
            ),
            # Western personal names (First Last) - more restrictive
            "western_person_name": re.compile(
                r"\b[A-Z][a-z]{3,}\s+[A-Z][a-z]{3,}\b(?=\s|$|[.,;:])"
            ),
            # Japanese addresses (postal code + prefecture + city)
            "jp_address": re.compile(
                r"〒?\d{3}-?\d{4}[都道府県市区町村]{1,3}[一-龯々\w\s]*", re.IGNORECASE
            ),
            # US addresses (street number + street + city + state + zip)
            "us_address": re.compile(
                r"\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl)\s*,?\s*[A-Za-z\s]+,?\s*[A-Z]{2}\s*\d{5}",
                re.IGNORECASE,
            ),
            # File paths (Windows, Unix, UNC paths)
            "file_path": re.compile(
                r'(?:[A-Za-z]:\\[^\s<>:"|?*]+|\\\\[^\s<>:"|?*\\]+\\[^\s<>:"|?*]*|\/[^\s<>:"|?*]+|\.\.?\/[^\s<>:"|?*]*)',
                re.IGNORECASE,
            ),
            # Function names (various programming languages)
            "function_name": re.compile(
                r"\b(?:function\s+|def\s+|const\s+|let\s+|var\s+)?([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(",
                re.IGNORECASE,
            ),
            # Class names (CamelCase) - more restrictive
            "class_name": re.compile(
                r"\b(?:class\s+|interface\s+|struct\s+|enum\s+)([A-Z][a-zA-Z0-9_]{2,})\b|(?<=class\s)[A-Z][a-zA-Z0-9_]{2,}\b"
            ),
            # Variable names with sensitive keywords
            "sensitive_variable": re.compile(
                r"\b(?:secret|password|passwd|key|token|auth|credential|private|confidential)[_-]?[a-zA-Z0-9_]*\s*[:=]",
                re.IGNORECASE,
            ),
            # Database table/column names
            "db_identifier": re.compile(
                r"\b(?:SELECT|INSERT|UPDATE|DELETE|FROM|INTO|SET|WHERE)\s+(?:\w+\.)?(\w+)\b",
                re.IGNORECASE,
            ),
            # Environment variables
            "env_variable": re.compile(
                r"\$\{?([A-Z][A-Z0-9_]*)\}?|\$([A-Z][A-Z0-9_]*)\b", re.IGNORECASE
            ),
            # Configuration keys
            "config_key": re.compile(
                r'\b([a-zA-Z][a-zA-Z0-9_.-]*)\s*[:=]\s*["\']?[^"\'\n]+["\']?',
                re.IGNORECASE,
            ),
            # URL parameters with sensitive data
            "url_parameter": re.compile(
                r"[?&](?:key|token|secret|password|auth|api_key|access_token)=([^&\s]+)",
                re.IGNORECASE,
            ),
            # License keys
            "license_key": re.compile(
                r"\b[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}\b", re.IGNORECASE
            ),
            # MAC addresses
            "mac_address": re.compile(
                r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b", re.IGNORECASE
            ),
            # UUID/GUID
            "uuid": re.compile(
                r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
                re.IGNORECASE,
            ),
            # 銀行口座番号（日本）- より具体的なパターン
            "jp_bank_account": re.compile(
                r"\b(?:口座|口座番号|account)[:：]\s*[0-9]{7,8}\b", re.IGNORECASE
            ),
            # IBAN（国際銀行口座番号）
            "iban": re.compile(
                r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b",
                re.IGNORECASE,
            ),
            # SWIFT/BICコード - コンテキスト必須
            "swift_bic": re.compile(
                r"(?:SWIFT|BIC|swift|bic)[:：]\s*([A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?)\b",
                re.IGNORECASE,
            ),
            # Bitcoin アドレス
            "bitcoin_address": re.compile(
                r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b|bc1[a-z0-9]{39,59}\b",
                re.IGNORECASE,
            ),
            # Ethereum アドレス
            "ethereum_address": re.compile(r"\b0x[a-fA-F0-9]{40}\b", re.IGNORECASE),
            # 日本の運転免許証番号
            "jp_license": re.compile(
                r"\b(?:免許|免許証|license)[:：]\s*[0-9]{12}\b", re.IGNORECASE
            ),
            # パスポート番号（一般的なフォーマット）
            "passport_number": re.compile(r"\b[A-Z]{1,2}[0-9]{6,9}\b", re.IGNORECASE),
            # 健康保険証番号（日本）
            "jp_health_insurance": re.compile(
                r"\b(?:保険証|健康保険|保険番号)[:：]\s*[0-9]{8}\b", re.IGNORECASE
            ),
            # 住民票コード（日本）
            "jp_resident_code": re.compile(
                r"\b(?:住民票|住民コード)[:：]\s*[0-9]{11}\b", re.IGNORECASE
            ),
            # 年金手帳番号（日本）
            "jp_pension_number": re.compile(
                r"\b(?:年金|年金番号|基礎年金番号)[:：]\s*[0-9]{4}-[0-9]{6}\b", re.IGNORECASE
            ),
            # 生年月日（様々な形式）
            "birth_date": re.compile(
                r"\b(?:生年月日|誕生日|生まれ|DOB|Date of Birth)[:：]\s*(?:[0-9]{4}[-/年][0-9]{1,2}[-/月][0-9]{1,2}日?|[0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{4})\b",
                re.IGNORECASE,
            ),
            # 血液型
            "blood_type": re.compile(
                r"\b(?:血液型|血液|Blood Type)[:：]\s*(?:[ABO]型?|AB型?|Rh[+-])\b",
                re.IGNORECASE,
            ),
            # 身長・体重
            "physical_info": re.compile(
                r"\b(?:身長|体重|Height|Weight)[:：]\s*[0-9]+(?:\.[0-9]+)?(?:cm|kg|ft|lb)\b",
                re.IGNORECASE,
            ),
            # 学籍番号・社員番号
            "id_number": re.compile(
                r"\b(?:学籍番号|社員番号|職員番号|Student ID|Employee ID)[:：]\s*[A-Za-z0-9]{4,12}\b",
                re.IGNORECASE,
            ),
            # 所属・部署情報
            "affiliation": re.compile(
                r"\b(?:所属|部署|Department|Division)[:：]\s*[^\r\n]{2,20}\b", re.IGNORECASE
            ),
            # 家族情報
            "family_info": re.compile(
                r"\b(?:配偶者|夫|妻|子供|父親|母親|兄弟|姉妹|家族|緊急連絡先)[:：]\s*[^\r\n]{2,30}\b",
                re.IGNORECASE,
            ),
            # 医療記録番号
            "medical_record": re.compile(
                r"\b(?:医療記録|患者番号|診察券|Patient ID|Medical Record)[:：]\s*[A-Za-z0-9]{4,15}\b",
                re.IGNORECASE,
            ),
            # 詳細住所（建物名・部屋番号）
            "detailed_address": re.compile(
                r"\b[0-9]+-[0-9]+-[0-9]+\s+[^\r\n]{5,30}(?:マンション|アパート|ビル|ハイツ|コーポ)[^\r\n]{0,20}\s*[0-9]{1,4}号?\b",
                re.IGNORECASE,
            ),
            # 最寄り駅情報
            "nearest_station": re.compile(
                r"\b(?:最寄り駅|最寄駅|駅)[:：]\s*[^\r\n]{2,20}(?:駅|Station)\b", re.IGNORECASE
            ),
            # URLパラメータ内のトークン
            "url_token": re.compile(
                r"[?&](?:token|access_token|auth_token|session_id|sid|key)=([A-Za-z0-9+/=_-]{10,})",
                re.IGNORECASE,
            ),
            # Azure Storage Keys
            "azure_storage_key": re.compile(r"\b[A-Za-z0-9+/]{88}==\b", re.IGNORECASE),
            # Google Cloud API Keys
            "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b", re.IGNORECASE),
            # Firebase keys
            "firebase_key": re.compile(
                r"\b[0-9]:[0-9]{11}:web:[a-fA-F0-9]{8,}\b", re.IGNORECASE
            ),
            # SSL証明書
            "ssl_certificate": re.compile(
                r"-----BEGIN CERTIFICATE-----[\s\S]*?-----END CERTIFICATE-----",
                re.IGNORECASE,
            ),
            # 公開鍵
            "public_key": re.compile(
                r"-----BEGIN PUBLIC KEY-----[\s\S]*?-----END PUBLIC KEY-----",
                re.IGNORECASE,
            ),
            # 日本の苗字（一般的な苗字）
            "japanese_surname": re.compile(
                r"\b(?:佐藤|鈴木|高橋|田中|伊藤|渡辺|山本|中村|小林|加藤|吉田|山田|"
                r"佐々木|山口|松本|井上|木村|林|斎藤|清水|山崎|森|池田|橋本|阿部|"
                r"石川|山下|中島|古川|藤田|後藤|岡田|長谷川|石井|村上|近藤|坂本|"
                r"遠藤|青木|藤井|西村|福田|太田|三浦|藤原|岡本|松田|中川|中野|"
                r"原田|小川|竹内|浜田|米田|安田|石田|大野|高木|武田|上田|杉山|"
                r"千葉|村田|河野|藤本|小野|田村|増田|小山|大塚|平野|島田|"
                r"前田|菅原|内田|和田|中田|石原|柴田|今井|酒井|宮本|神田|"
                r"森田|服部|野口|松井|菊地|新井|宮崎|渡部|森本|福島|"
                r"水野|平田|岩田|菅野|横山|工藤|中山|松尾|大西|"
                r"相馬|田口|島崎|金子|野村|川口|大橋|水田|白石|"
                r"森川|吉川|飯田|武井|永井|織田|川村|野田|松原)"
                r"(?=\s|さん|君|氏|様|$|[、。！？])",
                re.IGNORECASE,
            ),
            # 日本の名前（一般的な名前）
            "japanese_given_name": re.compile(
                r"\b(?:太郎|次郎|三郎|四郎|一郎|五郎|六郎|七郎|八郎|九郎|十郎|"
                r"花子|美子|幸子|恵子|智子|裕子|由美子|真理子|典子|洋子|"
                r"健|誠|学|勉|実|進|博|明|清|正|"
                r"美香|由香|香織|麻美|真美|直美|智美|美穂|美和|美樹|"
                r"大輔|雄一|雅弘|浩|武|茂|豊|修|隆|昭|"
                r"愛|恵|舞|綾|彩|香|美|希|恵美|恵理|"
                r"翔太|大樹|拓也|健太|翔|蓮|大翔|陸|颯太|湊|"
                r"結愛|陽菜|凛|葵|結菜|芽依|莉子|美桜|心春|桜|"
                r"優斗|悠斗|湊斗|陽斗|大和|律|樹|碧|颯|陽翔)"
                r"(?=\s|さん|君|氏|様|$|[、。！？])",
                re.IGNORECASE,
            ),
            # フルネーム（苗字+名前）の検出
            "japanese_full_name": re.compile(
                r"(?:氏名|名前|姓名|Name)[:：]\s*([一-龯ひ-ゖァ-ヺ]{2,4})\s*([一-龯ひ-ゖァ-ヺ]{1,4})\b",
                re.IGNORECASE,
            ),
            # 人名っぽいパターン（漢字2-4文字）
            "potential_name": re.compile(
                r"\b([一-龯]{2,4})\s*([一-龯]{1,4})(?=\s*(?:さん|君|氏|様|先生|殿|院長|部長|課長|主任|係長))",
                re.IGNORECASE,
            ),
            # 日本の都道府県（47都道府県すべて）
            "japanese_prefecture": re.compile(
                r"(?:北海道|青森県|岩手県|宮城県|秋田県|山形県|福島県|"
                r"茨城県|栃木県|群馬県|埼玉県|千葉県|東京都|神奈川県|"
                r"新潟県|富山県|石川県|福井県|山梨県|長野県|岐阜県|静岡県|愛知県|"
                r"三重県|滋賀県|京都府|大阪府|兵庫県|奈良県|和歌山県|"
                r"鳥取県|島根県|岡山県|広島県|山口県|"
                r"徳島県|香川県|愛媛県|高知県|"
                r"福岡県|佐賀県|長崎県|熊本県|大分県|宮崎県|鹿児島県|沖縄県)",
                re.IGNORECASE,
            ),
            # 政令指定都市と主要都市
            "japanese_major_city": re.compile(
                r"(?:札幌市|仙台市|さいたま市|千葉市|横浜市|川崎市|相模原市|新潟市|静岡市|浜松市|"
                r"名古屋市|京都市|大阪市|堺市|神戸市|岡山市|広島市|北九州市|福岡市|熊本市|"
                r"宇都宮市|前橋市|富山市|金沢市|福井市|甲府市|長野市|岐阜市|津市|大津市|"
                r"奈良市|和歌山市|鳥取市|松江市|山口市|徳島市|高松市|松山市|高知市|"
                r"佐賀市|長崎市|大分市|宮崎市|鹿児島市|那覇市|水戸市|青森市|盛岡市|秋田市|山形市|福島市)",
                re.IGNORECASE,
            ),
            # 東京23区
            "tokyo_ward": re.compile(
                r"(?:千代田区|中央区|港区|新宿区|文京区|台東区|墨田区|江東区|品川区|目黒区|"
                r"大田区|世田谷区|渋谷区|中野区|杉並区|豊島区|北区|荒川区|板橋区|練馬区|"
                r"足立区|葛飾区|江戸川区)",
                re.IGNORECASE,
            ),
            # 大阪の主要市
            "osaka_city": re.compile(
                r"(?:大阪市|堺市|東大阪市|枚方市|豊中市|吹田市|高槻市|茨木市|八尾市|寝屋川市|"
                r"平野区|住吉区|東住吉区|西成区|阿倍野区|住之江区|城東区|鶴見区|旭区|"
                r"都島区|福島区|此花区|西区|港区|大正区|天王寺区|浪速区|西淀川区|淀川区|"
                r"東淀川区|東成区|生野区|中央区|北区)",
                re.IGNORECASE,
            ),
            # 愛知県の主要市
            "aichi_city": re.compile(
                r"(?:名古屋市|豊田市|岡崎市|一宮市|瀬戸市|半田市|春日井市|豊川市|津島市|碧南市|"
                r"刈谷市|豊田市|安城市|西尾市|蒲郡市|犬山市|常滑市|江南市|小牧市|稲沢市|"
                r"新城市|東海市|大府市|知多市|知立市|尾張旭市|高浜市|岩倉市|豊明市|日進市)",
                re.IGNORECASE,
            ),
            # 神奈川県の主要市
            "kanagawa_city": re.compile(
                r"(?:横浜市|川崎市|相模原市|横須賀市|平塚市|鎌倉市|藤沢市|小田原市|茅ヶ崎市|逗子市|"
                r"三浦市|秦野市|厚木市|大和市|伊勢原市|海老名市|座間市|南足柄市|綾瀬市)",
                re.IGNORECASE,
            ),
            # 千葉県の主要市
            "chiba_city": re.compile(
                r"(?:千葉市|銚子市|市川市|船橋市|館山市|木更津市|松戸市|野田市|茂原市|成田市|"
                r"佐倉市|東金市|旭市|習志野市|柏市|勝浦市|市原市|流山市|八千代市|我孫子市)",
                re.IGNORECASE,
            ),
            # 埼玉県の主要市
            "saitama_city": re.compile(
                r"(?:さいたま市|川越市|熊谷市|川口市|行田市|秩父市|所沢市|飯能市|加須市|本庄市|"
                r"東松山市|春日部市|狭山市|羽生市|鴻巣市|深谷市|上尾市|草加市|越谷市|蕨市)",
                re.IGNORECASE,
            ),
            # 一般的な市区町村パターン（漢字2-4文字 + 市/区/町/村）
            "general_city": re.compile(r"([一-龯]{2,4})(市)", re.IGNORECASE),
            "general_ward": re.compile(r"([一-龯]{2,4})(区)", re.IGNORECASE),
            "general_town": re.compile(r"([一-龯]{2,4})(町)", re.IGNORECASE),
            "general_village": re.compile(r"([一-龯]{2,4})(村)", re.IGNORECASE),
        }

        return patterns

    def detect_all(
        self, text: str, min_confidence: float = 0.3
    ) -> List[SensitiveMatch]:
        """
        Detect all types of sensitive information in the given text.

        Args:
            text: The text to analyze
            min_confidence: Minimum confidence threshold for matches

        Returns:
            List of SensitiveMatch objects
        """
        matches = []

        for pattern_name, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                # Calculate confidence based on pattern type and context
                confidence = self._calculate_confidence(pattern_name, match, text)

                # Only include matches with sufficient confidence
                if confidence >= min_confidence:
                    sensitive_match = SensitiveMatch(
                        start=match.start(),
                        end=match.end(),
                        text=match.group(),
                        pattern_name=pattern_name,
                        confidence=confidence,
                    )
                    matches.append(sensitive_match)

        # Sort matches by position and remove overlapping matches
        matches = self._remove_overlapping_matches(matches)

        return matches

    def detect_specific(
        self, text: str, pattern_names: List[str], min_confidence: float = 0.3
    ) -> List[SensitiveMatch]:
        """
        Detect specific types of sensitive information.

        Args:
            text: The text to analyze
            pattern_names: List of pattern names to check
            min_confidence: Minimum confidence threshold for matches

        Returns:
            List of SensitiveMatch objects
        """
        matches = []

        for pattern_name in pattern_names:
            if pattern_name in self.patterns:
                pattern = self.patterns[pattern_name]
                for match in pattern.finditer(text):
                    confidence = self._calculate_confidence(pattern_name, match, text)

                    # Only include matches with sufficient confidence
                    if confidence >= min_confidence:
                        sensitive_match = SensitiveMatch(
                            start=match.start(),
                            end=match.end(),
                            text=match.group(),
                            pattern_name=pattern_name,
                            confidence=confidence,
                        )
                        matches.append(sensitive_match)

        matches = self._remove_overlapping_matches(matches)
        return matches

    def _calculate_confidence(
        self, pattern_name: str, match: re.Match, text: str
    ) -> float:
        """
        Calculate confidence score for a match based on context and pattern type.

        Args:
            pattern_name: Name of the pattern that matched
            match: The regex match object
            text: The full text being analyzed

        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = 0.8

        # Adjust confidence based on pattern type
        high_confidence_patterns = [
            "email",
            "credit_card",
            "ssn",
            "private_key",
            "mac_address",
            "uuid",
            "phone",
            "ip_address",
            "iban",
            "swift_bic",
            "bitcoin_address",
            "ethereum_address",
            "passport_number",
            "ssl_certificate",
            "public_key",
            "azure_storage_key",
            "google_api_key",
            "jp_health_insurance",
            "jp_resident_code",
            "jp_pension_number",
            "birth_date",
            "japanese_surname",
            "japanese_prefecture",  # 苗字と都道府県は高信頼度
        ]
        medium_confidence_patterns = [
            "api_key",
            "aws_access_key",
            "github_token",
            "jp_address",
            "us_address",
            "jp_person_name",
            "western_person_name",
            "file_path",
            "url_token",
            "firebase_key",
            "blood_type",
            "medical_record",
            "id_number",
            "detailed_address",
            "nearest_station",
            "japanese_given_name",
            "japanese_full_name",
            "japanese_major_city",
            "tokyo_ward",  # 名前と主要都市
        ]
        low_confidence_patterns = [
            "jp_bank_account",
            "jp_license",
            "physical_info",
            "affiliation",
            "family_info",
            "potential_name",
            "osaka_city",
            "aichi_city",
            "kanagawa_city",
            "chiba_city",
            "saitama_city",
            "general_city",
            "general_ward",
            "general_town",
            "general_village",  # 一般的な市区町村
        ]
        very_low_confidence_patterns = [
            "function_name",
            "class_name",
            "config_key",
            "sensitive_variable",
            "db_identifier",
            "env_variable",
        ]

        if pattern_name in high_confidence_patterns:
            base_confidence = 0.9
        elif pattern_name in medium_confidence_patterns:
            base_confidence = 0.7
        elif pattern_name in low_confidence_patterns:
            base_confidence = 0.5  # 偽陽性が多いパターンは低信頼度
        elif pattern_name in very_low_confidence_patterns:
            base_confidence = 0.2  # プログラム関連は非常に低い信頼度
        else:
            base_confidence = 0.6

        # Adjust based on context (simple heuristics)
        matched_text = match.group().lower()

        # Check for common false positives
        false_positive_indicators = [
            "test@test.com",
            "123-45-6789",
            "0000-0000-0000-0000",
            "your-api-key-here",
            "john doe",
            "jane smith",
            "foo bar",
            "test user",
            "c:\\temp\\",
            "/tmp/",  # nosec B108
            "example.txt",
            "test.py",
            "function_name",
            "class_name",
            "variable_name",
            # 一般的な英単語（偽陽性を防ぐ）
            "this is",
            "that was",
            "user credentials",
            "test python",
            "contact me",
            "just normal",
            "api key",
            "secret key",
        ]

        # 個人名パターンの特別な偽陽性チェック
        if pattern_name in [
            "jp_person_name",
            "western_person_name",
            "class_name",
            "function_name",
            "japanese_surname",
            "japanese_given_name",
            "potential_name",
        ]:
            # 一般的な英語の単語は名前として検出しない
            common_english_words = {
                "this",
                "that",
                "with",
                "have",
                "will",
                "from",
                "they",
                "know",
                "want",
                "been",
                "good",
                "much",
                "some",
                "time",
                "very",
                "when",
                "come",
                "here",
                "how",
                "just",
                "like",
                "long",
                "make",
                "many",
                "over",
                "such",
                "take",
                "than",
                "them",
                "well",
                "were",
                "what",
                "word",
                "work",
                "would",
                "write",
                "year",
                "your",
                "about",
                "after",
                "again",
                "back",
                "before",
                "being",
                "between",
                "both",
                "called",
                "came",
                "can",
                "could",
                "did",
                "different",
                "does",
                "don",
                "down",
                "each",
                "even",
                "every",
                "find",
                "first",
                "for",
                "get",
                "give",
                "great",
                "had",
                "has",
                "help",
                "her",
                "him",
                "his",
                "home",
                "house",
                "into",
                "its",
                "last",
                "left",
                "life",
                "live",
                "look",
                "made",
                "may",
                "men",
                "might",
                "more",
                "most",
                "move",
                "must",
                "name",
                "need",
                "never",
                "new",
                "next",
                "night",
                "now",
                "number",
                "off",
                "old",
                "only",
                "open",
                "other",
                "our",
                "out",
                "own",
                "part",
                "people",
                "place",
                "put",
                "right",
                "said",
                "same",
                "saw",
                "say",
                "see",
                "seem",
                "should",
                "show",
                "small",
                "sound",
                "still",
                "through",
                "too",
                "try",
                "turn",
                "two",
                "under",
                "until",
                "up",
                "use",
                "used",
                "using",
                "water",
                "way",
                "we",
                "where",
                "while",
                "who",
                "why",
                "without",
                "yes",
                "you",
                "young",
                "normal",
                "text",
                "information",
                "sensitive",
                "data",
                "content",
                "example",
                "test",
                "sample",
            }
            if matched_text in common_english_words:
                return 0.0  # 完全に信頼度を0にして除外

            # 日本語の一般的でない漢字組み合わせをチェック
            if pattern_name == "potential_name":
                # 推測による名前は更に信頼度を下げる
                base_confidence *= 0.5

            # 短い単語（4文字未満）は名前として信頼度を大幅に下げる（苗字は除く）
            if len(matched_text) < 4 and pattern_name != "japanese_surname":
                base_confidence *= 0.1

        for indicator in false_positive_indicators:
            if indicator in matched_text:
                base_confidence *= 0.3
                break

        # Check for context keywords that increase confidence
        context_start = max(0, match.start() - 50)
        context_end = min(len(text), match.end() + 50)
        context = text[context_start:context_end].lower()

        confidence_keywords = [
            "secret",
            "key",
            "token",
            "password",
            "auth",
            "credential",
            "private",
            "confidential",
            "sensitive",
            "personal",
            "name",
            "address",
            "location",
            "path",
            "file",
            "function",
            "class",
            "variable",
            "config",
            "setting",
            "parameter",
        ]

        for keyword in confidence_keywords:
            if keyword in context:
                base_confidence = min(1.0, base_confidence * 1.1)
                break

        return min(1.0, max(0.0, base_confidence))

    def _remove_overlapping_matches(
        self, matches: List[SensitiveMatch]
    ) -> List[SensitiveMatch]:
        """
        Remove overlapping matches, keeping the one with higher confidence.

        Args:
            matches: List of SensitiveMatch objects

        Returns:
            List of non-overlapping matches
        """
        if not matches:
            return matches

        # Sort by start position
        matches.sort(key=lambda x: x.start)

        result: List[SensitiveMatch] = []
        for current_match in matches:
            # Check for overlap with existing matches
            has_overlap = False
            for i, existing_match in enumerate(result):
                if (
                    current_match.start < existing_match.end
                    and current_match.end > existing_match.start
                ):
                    # There's an overlap
                    has_overlap = True
                    if current_match.confidence > existing_match.confidence:
                        # Replace the existing match with higher confidence one
                        result[i] = current_match
                    break

            if not has_overlap:
                result.append(current_match)

        return sorted(result, key=lambda x: x.start)

    def get_available_patterns(self) -> List[str]:
        """Get list of available pattern names."""
        return list(self.patterns.keys())

    def add_custom_pattern(
        self, name: str, pattern: str, flags: int = re.IGNORECASE
    ) -> None:
        """
        Add a custom pattern for detection.

        Args:
            name: Name for the pattern
            pattern: Regular expression pattern
            flags: Regex flags
        """
        self.patterns[name] = re.compile(pattern, flags)

    def remove_pattern(self, name: str) -> bool:
        """
        Remove a pattern from detection.

        Args:
            name: Name of the pattern to remove

        Returns:
            True if pattern was removed, False if it didn't exist
        """
        if name in self.patterns:
            del self.patterns[name]
            return True
        return False
