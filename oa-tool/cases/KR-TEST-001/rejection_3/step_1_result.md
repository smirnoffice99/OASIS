## 한국 특허 전문가 분석: 단일성 위반 거절이유 (특허법 제45조)

### 1. 심사관이 단일성 없다고 판단한 청구항 그룹 파악

심사관은 본 출원의 청구항 1~8항이 발명의 단일성 요건을 만족하지 않는다고 판단하였습니다.

*   **청구항 그룹 A:** 1~5항
    *   **그룹명:** 위치측정 방법
    *   **발명 카테고리:** 방법 (Method)
*   **청구항 그룹 B:** 6~8항
    *   **그룹명:** 단말 장치
    *   **발명 카테고리:** 장치 (Terminal device)

### 2. 인용문헌(D1) 확인

심사관이 단일성 판단에 사용한 인용문헌은 D1: US10,123,456 (공개일: 2022.03.15) 입니다.

**D1의 기술적 내용 및 핵심 발췌:**

D1은 무선 신호를 이용한 실내 위치 측정 시스템 및 방법에 관한 발명입니다. 특히, 위치 측정 방법(method claims)과 이를 구현하는 단말 장치(device claims) 모두를 개시하고 있습니다.

*   **D1의 발명의 명칭 및 요약:**
    *   Title: Location Measurement System Using Wireless Signals
    *   ABSTRACT: A system and method for indoor location measurement using multiple wireless signal types.
    *   *(분석: D1 자체가 시스템과 방법을 모두 다루고 있음을 명시합니다.)*

*   **D1의 청구항 1 (방법 클레임):**
    *   CLAIMS 1. A method for determining a location of a mobile device comprising: receiving wireless signals from a plurality of access points; computing a location estimation value from the received signals; and outputting a determined location.
    *   *(분석: D1은 위치 결정 방법을 청구하고 있습니다.)*

*   **D1의 위치 산출 수단/모듈 (장치 구성):**
    *   Column 3, Lines 15-40: "The location calculation means (positioning module) of the present invention receives RSSI data from surrounding access points and base stations. The positioning module processes the received signal data using a Kalman filter algorithm to produce a smoothed location estimate. The positioning module further incorporates a signal strength threshold to filter out unreliable measurements from distant transmitters. The output of the positioning module is a two-dimensional coordinate pair representing the estimated current location of the mobile device."
    *   *(분석: D1은 위치 계산을 수행하는 장치 구성요소(positioning module)를 개시하고 있습니다.)*

*   **D1의 기준값 산출 방법 (방법 구성):**
    *   Column 5, Lines 10-30: "The reference value calculation method of the present invention computes a location reference value as follows: first, RSSI values from at least three access points are collected simultaneously. Second, a distance estimate is computed from each RSSI value using a path loss model. Third, a weighted average of the distance estimates is computed, where weights are inversely proportional to estimated measurement uncertainty. This reference value calculation method provides improved accuracy compared to simple RSSI averaging approaches used in the prior art."
    *   *(분석: D1은 위치 기준값 산출 방법을 구체적으로 개시하고 있습니다.)*

*   **D1의 단말 장치 구현 (장치 구성):**
    *   Column 6, Lines 5-20: "The mobile terminal embodiment includes a wireless signal receiver module and a microprocessor running the location estimation algorithm. The terminal periodically updates its location estimate at a configurable refresh rate."
    *   *(분석: D1은 위치 측정 알고리즘을 실행하는 무선 신호 수신 모듈과 마이크로프로세서를 포함하는 이동 단말 장치를 개시하고 있습니다.)*

*   **D1의 한계점 (STF 식별에 중요):**
    *   Paragraphs [0045]-[0052]: "The reference value computation in this embodiment uses a fixed weighting scheme based on empirically determined coefficients. The weights do not adapt to changes in the signal environment or user behavior patterns. This is a known limitation of the present approach."
    *   *(분석: D1의 기준값 산출 방법은 고정된 가중치 방식을 사용하며, 신호 환경이나 사용자 행동 패턴에 따라 동적으로 조정되지 않는다는 한계를 명시하고 있습니다. 이는 본 출원 청구항 7의 "dynamically adjusted according to a user movement pattern"과 대비될 수 있는 부분입니다.)*

**인용문헌 D1이 개시하지 않는 기술 (본 출원의 잠재적 STF):**

D1은 다음을 명시적으로 개시하지 않습니다.
*   관성 센서(IMU) 데이터와의 융합 (Fusion with inertial sensor (IMU) data)
*   핸드오버 이벤트 발생 시 기준값 재산출 (Re-calculation of reference values upon handover events)
*   RSSI, RTT, AoA를 동시에 결합한 가중 평균 (Weighted average combining RSSI, RTT, and AoA simultaneously)
*   사용자 이동 패턴에 따른 측위 기준값의 동적 조정 (Dynamic adjustment of positioning reference values based on user movement patterns)

### 3. 심사관의 STF 부재 논거 요약

심사관은 청구항 1~8항이 발명의 단일성 요건을 만족하지 않는다고 판단하며, 그 근거는 다음과 같습니다.

*   **심사관 의견 원문:**
    "청구항 그룹 A(1~5항)와 그룹 B(6~8항)는 인용발명 D1에 비하여 개선된 공통의 특별한 기술적 특징(STF, Special Technical Feature)을 공유하지 않습니다. D1은 위치 측정 방법(방법 클레임)과 이를 구현하는 단말 장치(장치 클레임) 모두를 개시하고 있어, 그룹 A와 그룹 B 각각이 D1에 대해 독립적으로 신규하거나 진보적인 특징을 가지더라도, 양 그룹 간에 D1 대비 개선된 공통 STF가 존재하지 않으므로 단일성이 없습니다."

*   **심사관 논거의 핵심 포인트:**
    1.  **공통 STF 부재:** 청구항 그룹 A (방법)와 그룹 B (장치)는 인용발명 D1에 비해 *개선된* 공통의 특별한 기술적 특징(STF)을 공유하지 않는다.
    2.  **D1의 포괄성:** 인용발명 D1은 이미 위치 측정 방법과 이를 구현하는 단말 장치 *모두*를 개시하고 있다.
    3.  **개선된 STF의 필요성:** 심사관은 각 그룹이 D1에 대해 개별적으로 신규하거나 진보적인 특징을 가질 수 있음을 인정하면서도, 두 그룹을 묶는 *D1 대비 개선된 공통 STF*가 없기 때문에 단일성이 없다고 판단한다. 즉, 단순히 방법과 장치가 서로 대응된다는 것만으로는 D1 대비 개선된 공통 STF가 될 수 없다는 입장이다.