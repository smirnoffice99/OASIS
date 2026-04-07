## Step 2: 인용발명 분석

### 인용문헌 D1: US10,123,456

**분석 대상 청구항:** 청구항 1

**청구항 1의 구성요소 분석:**

1.  **`collecting a plurality of wireless signals`**
    *   **인용문헌 발췌:**
        *   "ABSTRACT: A system and method for indoor location measurement using multiple wireless signal types."
        *   "CLAIMS 1: A method for determining a location of a mobile device comprising: receiving wireless signals from a plurality of access points;"
        *   "Column 3, Lines 15-40: The location calculation means (positioning module) of the present invention receives RSSI data from surrounding access points and base stations."
        *   "Column 4, Lines 1-25: The system architecture comprises three main components: a signal collector, a signal processor, and a location output unit. The signal collector continuously scans available wireless channels."
        *   "Column 5, Lines 10-30: The reference value calculation method of the present invention computes a location reference value as follows: first, RSSI values from at least three access points are collected simultaneously."
    *   **기술적 의미:** D1은 실내 위치 측정을 위해 다수의 무선 신호(예: RSSI 데이터)를 주변 액세스 포인트 및 기지국으로부터 수집하는 기술을 개시한다. 신호 수집기(signal collector)가 무선 채널을 지속적으로 스캔하여 신호를 수신한다.
    *   **유사점 및 차이점의 가능성:** 본원 청구항 1의 "collecting a plurality of wireless signals"는 D1의 "receiving wireless signals from a plurality of access points" 및 "receives RSSI data from surrounding access points and base stations"와 실질적으로 동일한 기술적 사상을 포함하는 것으로 보인다.

2.  **`calculating a first positioning reference value based on the collected wireless signals`**
    *   **인용문헌 발췌:**
        *   "CLAIMS 1: A method for determining a location of a mobile device comprising: ... computing a location estimation value from the received signals;"
        *   "Column 3, Lines 15-40: The positioning module processes the received signal data using a Kalman filter algorithm to produce a smoothed location estimate."
        *   "Column 5, Lines 10-30: The reference value calculation method of the present invention computes a location reference value as follows: first, RSSI values from at least three access points are collected simultaneously. Second, a distance estimate is computed from each RSSI value using a path loss model. Third, a weighted average of the distance estimates is computed, where weights are inversely proportional to estimated measurement uncertainty. This reference value calculation method provides improved accuracy compared to simple RSSI averaging approaches used in the prior art."
    *   **기술적 의미:** D1은 수집된 무선 신호(RSSI)를 기반으로 "location reference value"를 계산하는 방법을 개시한다. 이 방법은 RSSI로부터 거리 추정치를 계산하고, 이 거리 추정치들의 가중 평균을 계산하여 기준값을 도출한다. 이는 최종 위치 추정의 중간 단계로 사용될 수 있다.
    *   **유사점 및 차이점의 가능성:** 본원 청구항 1의 "calculating a first positioning reference value based on the collected wireless signals"는 D1의 "computing a location estimation value from the received signals" 및 "computes a location reference value as follows: ... a weighted average of the distance estimates is computed"와 매우 유사하다. D1은 수집된 무선 신호(RSSI)를 기반으로 위치 기준값을 계산하는 구체적인 방법을 제시하고 있다.

3.  **`determining a position by fusing the first positioning reference value with inertial sensor data`**
    *   **인용문헌 발췌:**
        *   "CLAIMS 1: A method for determining a location of a mobile device comprising: ... outputting a determined location."
        *   "Column 3, Lines 15-40: The output of the positioning module is a two-dimensional coordinate pair representing the estimated current location of the mobile device."
        *   "NOTE: This prior art document does NOT disclose: ... Fusion with inertial sensor (IMU) data"
    *   **기술적 의미:** D1은 무선 신호 처리(예: 칼만 필터)를 통해 위치를 결정하고 출력하는 것을 개시하지만, 관성 센서 데이터(inertial sensor data)와의 융합(fusing)을 통해 위치를 결정하는 내용은 전혀 언급하고 있지 않다.
    *   **유사점 및 차이점의 가능성:** 본원 청구항 1의 "determining a position by fusing the first positioning reference value with inertial sensor data"는 D1에 명확히 개시되어 있지 않다. D1은 무선 신호만을 사용하여 위치를 결정하는 것으로 보이며, 관성 센서 데이터와의 융합을 통한 위치 결정은 D1과 명확한 차이점으로 판단된다.

### 인용문헌 D2: US9,876,543

**분석 대상 청구항:** 청구항 1

**청구항 1의 구성요소 분석:**

1.  **`collecting a plurality of wireless signals`**
    *   **인용문헌 발췌:**
        *   "ABSTRACT: A wireless signal processing method that computes positioning metrics from heterogeneous signal sources for mobile device location estimation."
        *   "CLAIMS 1: A signal processing method for positioning comprising: collecting heterogeneous wireless signals;"
        *   "Paragraph [0045]-[0052]: The reference value calculation step of the present invention operates as follows: - Step 1: Collect RSSI measurements from visible Wi-Fi access points. - Step 2: Collect RTT measurements where supported by the access point hardware."
    *   **기술적 의미:** D2는 모바일 장치 위치 추정을 위해 이종(heterogeneous) 무선 신호 소스로부터 신호를 수집하는 방법을 개시한다. 구체적으로 RSSI 및 RTT 측정값을 수집한다.
    *   **유사점 및 차이점의 가능성:** 본원 청구항 1의 "collecting a plurality of wireless signals"는 D2의 "collecting heterogeneous wireless signals" 및 "Collect RSSI measurements ... Collect RTT measurements"와 실질적으로 동일한 기술적 사상을 포함하는 것으로 보인다.

2.  **`calculating a first positioning reference value based on the collected wireless signals`**
    *   **인용문헌 발췌:**
        *   "CLAIMS 1: A signal processing method for positioning comprising: ... computing a positioning metric from the collected signals;"
        *   "Paragraph [0045]-[0052]: The reference value calculation step of the present invention operates as follows: ... - Step 3: Apply a pre-defined weighting table to combine RSSI and RTT into a single composite reference value. - Step 4: Apply a low-pass filter to smooth the composite reference value over a sliding window of N measurements."
    *   **기술적 의미:** D2는 수집된 이종 무선 신호(RSSI, RTT)를 기반으로 "composite reference value"라는 위치 측정 지표(positioning metric)를 계산하는 방법을 개시한다. 이는 사전 정의된 가중치 테이블을 사용하여 RSSI와 RTT를 결합하고, 저역 통과 필터를 적용하여 평활화한다.
    *   **유사점 및 차이점의 가능성:** 본원 청구항 1의 "calculating a first positioning reference value based on the collected wireless signals"는 D2의 "computing a positioning metric from the collected signals" 및 "combine RSSI and RTT into a single composite reference value"와 매우 유사하다. D2는 수집된 무선 신호(RSSI, RTT)를 기반으로 복합 기준값을 계산하는 구체적인 방법을 제시하고 있다.

3.  **`determining a position by fusing the first positioning reference value with inertial sensor data`**
    *   **인용문헌 발췌:**
        *   "CLAIMS 1: A signal processing method for positioning comprising: ... providing the positioning metric to a location estimation module."
        *   "Paragraph [0030]-[0040]: The invention uses a two-step process: (1) individual signal type processing and (2) metric fusion. Each signal type is processed independently to produce a preliminary position estimate, then these estimates are combined using a fixed fusion algorithm."
        *   "NOTE: This prior art document does NOT disclose: ... Integration with inertial sensor data"
    *   **기술적 의미:** D2는 위치 측정 지표(positioning metric)를 위치 추정 모듈에 제공하고, 개별 신호 유형으로부터 얻은 예비 위치 추정치를 고정된 융합 알고리즘을 사용하여 결합하는 것을 개시한다