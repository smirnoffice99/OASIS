## 인용발명 분석

### 인용발명 1: 미국 특허출원공개공보 US2020/0008185호 (D1)

**1. 인용발명 요약**

인용발명 1(D1)은 무선 통신 시스템에서 분산형 자원 유닛(Distributed Resource Unit, RU) 할당 기술에 관한 것으로, 특히 직교 주파수 분할 다중 접속(OFDMA) 시스템에서 전력 스펙트럼 밀도(PSD) 제한을 완화하고 전송 전력을 증가시키기 위해 인접 톤(contiguous tones)을 비-인접 톤(non-contiguous tones)으로 맵핑하여 사용하는 방법을 개시합니다.

*   **RU 및 톤 계획 (RU and Tone Plan):**
    *   D1은 무선 매체를 통해 물리 계층 수렴 프로토콜 프로토콜 데이터 유닛(PPDU)을 송신하기 위한 RU를 할당(선택)하는 것을 개시합니다 (단락 [0058], [0059]).
    *   RU는 주파수 스펙트럼에 대한 톤 계획의 일부분을 포함하며, RU 대역폭에 걸쳐 있는 인접 톤들의 세트를 포함합니다 (단락 [0105]-[0107], 도 8).
    *   D1은 RU26, RU52, RU106 등 다양한 RU 유형을 예시합니다 (단락 [0106], [0133]).
    *   주파수 스펙트럼은 80 MHz 대역을 포함할 수 있으며, 선택된 RU는 약 10 MHz 이하의 대역폭을 가질 수 있습니다 (단락 [0134]).

*   **톤 맵핑 및 비-인접 톤 송신 (Tone Mapping and Non-contiguous Tone Transmission):**
    *   D1은 선택된 RU의 인접 톤 세트를 주파수 스펙트럼에 걸쳐 분산된 비-인접 톤 세트에 맵핑하는 것을 개시합니다 (단락 [0108]-[0109], 도 9).
    *   이 맵핑은 톤 맵핑 거리(DTM)를 사용하여 수행될 수 있습니다 (단락 [0121]).
    *   DTM은 비-인접 톤 세트의 인접 톤들 사이의 거리 또는 간격을 나타낼 수 있습니다 (단락 [0122]).
    *   맵핑된 비-인접 톤 세트를 통해 PPDU를 송신합니다 (단락 [0060]).
    *   비-인접 톤들은 주파수 스펙트럼 전체에 걸쳐 서로 인터리빙될 수 있습니다 (단락 [0117], [0124]).
    *   DTM은 톤 계획의 각 RU의 인접 톤을 주파수 스펙트럼에 걸쳐 분산된 해당 비-인접 및 비-펑처드 톤 세트에 맵핑하도록 구성될 수 있습니다 (단락 [0123]).
    *   맵핑은 선택된 RU의 각 톤과 DTM의 곱셈으로부터 맵핑된 톤 인덱스를 얻는 것을 포함할 수 있습니다 (단락 [0128]).
    *   파일럿 톤도 DTM을 사용하여 비-인접 톤 세트에 맵핑될 수 있습니다 (단락 [0132]).

*   **PPDU 유형 및 통신 시나리오 (PPDU Types and Communication Scenarios):**
    *   PPDU는 하향링크(DL) 또는 상향링크(UL) 전송에 사용될 수 있습니다 (단락 [0061]).
    *   PPDU는 단일 사용자(SU) 또는 다중 사용자(MU) 전송에 사용될 수 있습니다 (단락 [0062]).
    *   PPDU는 OFDMA 또는 MU-MIMO 전송에 사용될 수 있습니다 (단락 [0063]).
    *   PPDU는 트리거 기반(TB) PPDU일 수 있으며, RU는 무선 통신 디바이스가 수신한 트리거 프레임에 의해 지시될 수 있습니다 (단락 [0064], [0065]).

*   **펑처링 (Puncturing):**
    *   비-인접 톤 세트는 펑처드 주파수 서브밴드와 관련된 톤들을 제외할 수 있습니다 (단락 [0130]).
    *   주파수 스펙트럼은 톤 계획에서 펑처링되지 않은 톤들의 수와 연관될 수 있습니다 (단락 [0131]).
    *   D1은 펑처링된 톤에서도 데이터를 송신할 수 있음을 언급합니다 (단락 [0057], "station 504 and/or AP 502 are configured to transmit data 1022 with subcarriers (or tones) punctured").

**2. 심사관 지적 사항 관련 D1 내용**

*   **청구항 1의 구성 1 (RU 선택):**
    *   "The HE or EHT frame may be a physical Layer Convergence Procedure (PLCP) Protocol Data Unit (PPDU)." (단락 [0057])
    *   "An allocation of a bandwidth or a number of tones or sub-carriers may be termed a resource unit (RU) allocation in accordance with some embodiments." (단락 [0058])
    *   "The RUs 800 and 900 are examples of RUs that may be allocated for transmission of a PPDU." (단락 [0059])
    *   "The tone plan 800 includes a plurality of RUs, such as RU26, RU52, and RU106. Each RU includes a set of contiguous tones spanning a bandwidth of the RU." (단락 [0106]-[0107], 도 8)
    *   D1은 PPDU 송수신을 위한 RU 할당(선택) 및 선택된 RU가 주파수 스펙트럼의 톤 계획 일부분을 포함하고 인접 톤 세트를 포함함을 개시합니다.

*   **청구항 1의 구성 2 (DTM을 이용한 비-인접 톤 맵핑):**
    *   "The tone mapping may be performed using a tone mapping distance (DTM)." (단락 [0121])
    *   "Each distributed RU is formed by a set of non-contiguous tones that are spread across the channel bandwidth." (단락 [0109])
    *   "The DTM may be configured for mapping contiguous tones of each RU in the tone plan to a corresponding set of non-contiguous and non-punctured tones distributed across the frequency spectrum." (단락 [0123])
    *   D1은 DTM을 사용하여 인접 톤을 주파수 스펙트럼에 걸쳐 분산된 비-인접 톤 세트에 맵핑하는 것을 개시합니다. 다만, 심사관은 "주파수 스펙트럼 전체에 적용 가능한 DTM"이라는 점이 명시적으로 없다고 지적합니다.

*   **청구항 1의 구성 3 (PPDU 송신):**
    *   "A station 504 and/or AP 502 are configured to transmit a PPDU on one of the distributed RUs and contiguous RUs 800, 900 disclosed in FIGS. 8 and 9." (단락 [0060])
    *   D1은 주파수 스펙트럼에 걸쳐 분산된 비-인접 톤 세트를 통해 PPDU를 송신하는 것을 개시합니다.

*   **청구항 2-4 (PPDU 유형, 트리거 프레임):**
    *   "The RUs 800 and 900 may be allocated for UL or DL transmissions." (단락 [0061])
    *   "The RUs 800 and 900 may be allocated for SU or MU transmissions." (단락 [0062])
    *   "The RUs 800 and 900 may be allocated for OFDMA or MU-MIMO transmissions." (단락 [0063])
    *   "The RUs 800 and 900 may be allocated for trigger-based (TB) PPDU transmissions." (단락 [0064])
    *   "The RUs 800 and 900 may be indicated by a trigger frame received by the wireless communication device." (단락 [0065])
    *   D1은 DL OFDMA, MU-MIMO, SU PPDU, TB PPDU, 트리거 프레임에 의해 지시되는 RU를 개시합니다.

*   **청구항 5 (비-펑처드 톤):**
    *   "The frequency spectrum may be associated with a number of non-punctured tones in the tone plan." (단락 [0131])
    *   "The set of non-contiguous tones may exclude tones associated with punctured frequency subbands." (단락 [0130])
    *   D1은 비-펑처드 톤과 관련된 주파수 스펙트럼을 개시합니다.

*   **청구항 6 (파일럿 톤 맵핑):**
    *   "The mapping may include mapping pilot tones of the selected RU to the set of non-contiguous tones using the DTM." (단락 [0132])
    *   D1은 파일럿 톤 맵핑을 개시합니다.

*   **청구항 10-12, 31-33 (DTM 값, RU 대역폭, RU 유형):**
    *   "The DTM may be 13." (단락 [0125])
    *   "Each tone of the set of non-contiguous tones may occupy a unique 1 MHz frequency subband." (단락 [0126])
    *   "The tones of the set of contiguous tones may be mapped in groups of N tones to the set of non-contiguous tones distributed across the frequency spectrum, wherein N is an integer greater than one." (단락 [0127])
    *   "The mapping may comprise obtaining a mapped tone index for each tone of the set of non-contiguous tones from a multiplication of a respective tone of the selected RU and the DTM." (단락 [0128])
    *   "The frequency spectrum may span an 80 MHz frequency band, and the selected RU may span a frequency band less than or equal to approximately 10 MHz." (단락 [0134])
    *   "The tone plan may include one or more of RU26, RU52, RU106, RU242, RU484, or RU996 resource units." (단락 [0133])
    *   D1은 구체적인 DTM 값, 톤 대역폭, N개 톤 그룹 맵핑, 맵핑된 톤 인덱스 획득, 주파수 스펙트럼 및 RU 대역폭, RU 유형 등을 개시합니다.

*   **청구항 13-20, 34-52 (장치 발명, UL 송신):**
    *   D1은 장치에 의한 무선 통신 방법 및 UL 송신에 대한 내용을 포함하고 있어, 청구항 13-20 및 34-52의 기술적 사상과 실질적으로 동일하거나 대응되는 내용을 개시합니다 (예: 단락 [0060]의 "station 504 and/or AP 502 are configured to transmit...", 단락 [0061]의 "UL or DL transmissions").

### 인용발명 2: 미국 특허출원공개공보 US2020/0014509호 (D2)

**1. 인용발명 요약**

인용발명 2(D2)는 인용발명 1과 유사하게 무선 통신 시스템에서 분산형 자원 유닛(RU) 할당 기술에 관한 것으로, 인접 톤을 비-인접 톤으로 맵핑하여 전송 전력을 효율적으로 활용하는 방법을 개시합니다. D1과 많은 부분이 중복되지만, D2는 특히 DTM의 적용 범위 및 톤 분산 방식에 대해 더 구체적인 설명을 제공합니다.

*   **RU 및 톤 계획 (RU and Tone Plan):**
    *   D2는 무선 매체를 통해 PPDU를 송신하기 위한 RU를 할당(선택)하는 것을 개시합니다 (단락 [0086]).
    *   RU는 주파수 스펙트럼에 대한 톤 계획의 일부분을 포함하며, RU 대역폭에 걸쳐 있는 인접 톤들의 세트를 포함합니다 (단락 [0121]-[0122], 도 7).
    *   D2는 RU26, RU52, RU106 등 다양한 RU 유형을 예시합니다 (단락 [0121], [0137]).
    *   주파수 스펙트럼은 80 MHz 대역을 포함할 수 있으며, 선택된 RU는 약 10 MHz 이하의 대역폭을 가질 수 있습니다 (단락 [0138]).

*   **톤 맵핑 및 비-인접 톤 송신 (Tone Mapping and Non-contiguous Tone Transmission):**
    *   D2는 선택된 RU의 인접 톤 세트를 주파수 스펙트럼에 걸쳐 분산된 비-인접 톤 세트에 맵핑하는 것을 개시합니다 (단락 [0123]-[0124], 도 8).
    *   이 맵핑은 톤 맵핑 거리(DTM)를 사용하여 수행될 수 있습니다 (단락 [0126]).
    *   DTM은 비-인접 톤 세트의 인접 톤들 사이의 거리 또는 간격을 나타낼 수 있습니다 (단락 [0127]).
    *   맵핑된 비-인접 톤 세트를 통해 PPDU를 송신합니다 (단락 [0086]).
    *   비-인접 톤들은 주파수 스펙트럼 전체에 걸쳐 서로 인터리빙될 수 있습니다 (단락 [0125], [0129]).
    *   DTM은 톤 계획의 각 RU의 인접 톤을 주파수 스펙트럼에 걸쳐 분산된 해당 비-인접 및 비-펑처드 톤 세트에 맵핑하도록 구성될 수 있습니다 (단락 [0128]).
    *   맵핑은 선택된 RU의 각 톤과 DTM의 곱셈으로부터 맵핑된 톤 인덱스를 얻는 것을 포함할 수 있습니다 (단락 [0133]).
    *   파일럿 톤도 DTM을 사용하여 비-인접 톤 세트에 맵핑될 수 있습니다 (단락 [0136]).

*   **DTM의 전체 스펙트럼 적용 및 톤 분산 상세 (DTM Applicability to Entire Spectrum and Detailed Tone Spreading):**
    *   D2는 RU가 주파수에서 간격으로 분리된 두 개 이상의 부분으로 분할될 수 있음을 명시합니다 (단락 [0139]).
    *   비-인접 톤 세트의 인접 톤들이 간격으로 분리될 수 있음을 명시합니다 (단락 [0140]).
    *   톤 맵핑 구성이 동일한 RU26을 구성하는 파일럿 톤들의 균일한 간격 분리를 지원할 수 있음을 개시합니다 (단락 [0141]).
    *   파일럿 신호가 채널 대역폭 전체에 균일하게 분산되도록 할당될 수 있음을 개시합니다 (단락 [0142]).
    *   최소 맵핑 거리(예: 전체 전력 이점을 얻기 위함)는 채널 대역폭에 대한 논리 RU 크기에 따라 달라질 수 있음을 개시합니다 (단락 [0143]). 이러한 설명들은 DTM이 채널 대역폭 전체에 걸쳐 적용되어 톤을 분산시키는 개념을 뒷받침합니다.

*   **PPDU 유형 및 통신 시나리오 (PPDU Types and Communication Scenarios):**
    *   D2는 D1과 유사하게 UL/DL, SU/MU, OFDMA/MU-MIMO, TB PPDU 및 트리거 프레임에 대한 내용을 포함합니다 (단락 [0086]).

**2. 심사관 지적 사항 관련 D2 내용**

*   **청구항 1의 구성 2 (DTM을 이용한 비-인접 톤 맵핑 - 주파수 스펙트럼 전체 적용):**
    *   심사관은 D1에 명시적으로 없는 "주파수 스펙트럼 전체에 적용 가능한 DTM"이라는 차이 구성에 대해 D2의 "분산 매핑을 위해 주파수 스펙트럼 또는 채널 대역폭 전체에 적용 가능한 톤 매핑 거리를 사용하는 점"을 결합하여 쉽게 도출될 수 있다고 주장합니다.
    *   D2는 "The DTM may be configured for mapping contiguous tones of each RU in the tone plan to a corresponding set of non-contiguous and non-punctured tones distributed across the frequency spectrum." (단락 [0128])와 같이 D1과 유사한 표현을 사용합니다.
    *   그러나 D2는 "The system may allocate pilot tones 935 such that pilot signals for each user (for example, each STA) are evenly spread over the channel bandwidth 905" (단락 [0142]) 및 "A minimum mapping distance (for example, to achieve the full power advantage) may depend on the logic RU size for the channel bandwidth 715" (단락 [0143])와 같이, DTM이 채널 대역폭(즉, 주파수 스펙트럼) 전체에 걸쳐 톤을 균일하게 분산시키고 전력 이점을 얻기 위해 적용되는 개념을 더욱 명확히 제시합니다. 이는 DTM이 주파수 스펙트럼 전체에 걸쳐 적용 가능함을 암시합니다.

*   **청구항 2-4 (PPDU 유형, 트리거 프레임):**
    *   "A wireless device, such as an AP and/or a STA, may use a map to map each RU 310 to a respective non-contiguous set of tones... The STA may receive an indictor (for example, an RU value) indicating an RU assigned to the STA (for example, in a trigger frame or in a downlink transmission) from an AP..." (단락 [0086])
    *   D2는 MU-OFDMA, MU-MIMO, 트리거 프레임에서 지시되는 RU 할당 등을 개시하여 청구항 2-4의 내용을 뒷받침합니다.

*   **청구항 5 (비-펑처드 톤):**
    *   "The set of non-contiguous tones may exclude tones associated with punctured frequency subbands." (단락 [0134])
    *   "The frequency spectrum may be associated with a number of non-punctured tones in the tone plan." (단락 [0135])
    *   D2는 데이터 송신에 사용되는 펑처링 되지 않는 톤들을 개시합니다.

*   **청구항 6 (파일럿 톤 맵핑):**
    *   "The mapping may include mapping pilot tones of the selected RU to the set of non-contiguous tones using the DTM." (단락 [0136])
    *   D2는 할당되는 RU의 파일럿 톤들이 비-인접 톤들 세트에 맵핑되는 점을 개시합니다.

*   **청구항 7-9 (DTM 구성, 톤 간격, 인터리빙):**
    *   "the RU may be split into two or more portions separated by gaps in frequency" (단락 [0139])
    *   "adjacent tones in the non-contiguous set of tones for RU 310-c may be separated by spaces (in other words, gaps)" (단락 [0140])
    *   "This tone mapping configuration 900-b may support even spacing for separation of the pilot tones 935 composing a same RU26" (단락 [0141])
    *   "the system may allocate pilot tones 935 such that pilot signals for each user (for example, each STA) are evenly spread over the channel bandwidth 905" (단락 [0142])
    *   "A minimum mapping distance (for example, to achieve the full power advantage) may depend on the logic RU size for the channel bandwidth 715" (단락 [0143])
    *   D2는 RU가 간격으로 분할되고, 인접 톤들이 간격으로 분리되며, 파일럿 톤들이 균일하게 분산되고, 최소 맵핑 거리가 채널 대역폭에 따라 결정되는 등 DTM의 구성 및 톤 간격에 대한 상세한 내용을 개시합니다.

*   **청구항 10-12, 31-33 (DTM 값, RU 대역폭, RU 유형):**
    *   "The DTM may be 13." (단락 [0130])
    *   "Each tone of the set of non-contiguous tones may occupy a unique 1 MHz frequency subband." (단락 [0131])
    *   "The tones of the set of contiguous tones may be mapped in groups of N tones to the set of non-contiguous tones distributed across the frequency spectrum, wherein N is an integer greater than one." (단락 [0132])
    *   "The mapping may comprise obtaining a mapped tone index for each tone of the set of non-contiguous tones from a multiplication of a respective tone of the selected RU and the DTM." (단락 [0133])
    *   "The frequency spectrum may span an 80 MHz frequency band, and the selected RU may span a frequency band less than or equal to approximately 10 MHz." (단락 [0138])
    *   "The tone plan may include one or more of RU26, RU52, RU106, RU242, RU484, or RU996 resource units." (단락 [0137])
    *   D2는 D1과 유사하게 구체적인 DTM 값, 톤 대역폭, N개 톤 그룹 맵핑, 맵핑된 톤 인덱스 획득, 주파수 스펙트럼 및 RU 대역폭, RU 유형 등을 개시합니다.

*   **청구항 13-20, 34-52 (장치 발명, UL 송신):**
    *   D2는 장치에 의한 무선 통신 방법 및 UL 송신에 대한 내용을 포함하고 있어, 청구항 13-20 및 34-52의 기술적 사상과 실질적으로 동일하거나 대응되는 내용을 개시합니다 (예: 단락 [0086]의 "A wireless device, such as an AP and/or a STA, may use a map to map each RU 310 to a respective non-contiguous set of tones...").