## [Step 3: 차이점 분석 및 진보성 논거 도출]

### 1. 구조적 차이점 특정 (독립항 기준)

본원발명 청구항 1의 각 구성요소와 인용발명 D1 및 D2의 대응 구성을 비교한 결과, 다음과 같은 구조적 차이점이 식별됩니다.

*   **본원발명 청구항 1의 구성요소 (A) 및 (B)와 인용발명 D1 및 D2의 대응 구성은 실질적으로 동일하거나 유사합니다.**
    *   **구성요소 (A): "collecting a plurality of wireless signals"**
        *   **본원발명:** 단말 장치가 주변 환경으로부터 복수의 무선 신호(예: Wi-Fi, Bluetooth, cellular signals 등)를 수집하는 단계.
        *   **인용발명 D1:** "receiving wireless signals from a plurality of access points" (CLAIMS 1), "receives RSSI data from surrounding access points and base stations" (Column 3, Lines 15-40). D1은 실내 위치 측정을 위해 다수의 무선 신호(RSSI)를 수집하는 것을 개시합니다.
        *   **인용발명 D2:** "collecting heterogeneous wireless signals" (CLAIMS 1), "Collect RSSI measurements from visible Wi-Fi access points. - Step 2: Collect RTT measurements where supported by the access point hardware." (Paragraph [0045]-[0052]). D2는 이종 무선 신호(RSSI, RTT)를 수집하는 것을 개시합니다.
        *   **결론:** 본원발명 (A)는 D1 및 D2의 대응 구성과 실질적으로 동일합니다.
    *   **구성요소 (B): "calculating a first positioning reference value based on the collected wireless signals"**
        *   **본원발명:** 구성요소 (A)에서 수집된 복수의 무선 신호들을 기반으로, 위치 측정에 활용될 수 있는 제1 측위 기준값(first positioning reference value)을 산출하는 단계. 명세서 [0002]에 따라 RSSI, RTT, AoA 중 적어도 하나를 포함하는 가중 평균값으로 정의될 수 있습니다.
        *   **인용발명 D1:** "computing a location estimation value from the received signals" (CLAIMS 1), "computes a location reference value as follows: ... a weighted average of the distance estimates is computed" (Column 5, Lines 10-30). D1은 수집된 무선 신호(RSSI)를 기반으로 거리 추정치의 가중 평균을 계산하여 위치 기준값을 도출하는 것을 개시합니다.
        *   **인용발명 D2:** "computing a positioning metric from the collected signals" (CLAIMS 1), "combine RSSI and RTT into a single composite reference value" (Paragraph [0045]-[0052]). D2는 수집된 이종 무선 신호(RSSI, RTT)를 기반으로 "composite reference value"라는 위치 측정 지표를 계산하는 것을 개시합니다.
        *   **결론:** 본원발명 (B)는 D1 및 D2의 대응 구성과 실질적으로 동일합니다.

*   **본원발명 청구항 1의 구성요소 (C)는 인용발명 D1 및 D2에 개시되어 있지 않습니다.**
    *   **본원발명 (C): "determining a position by fusing the first positioning reference value with inertial sensor data"**
        *   **인용발명 D1:** D1은 무선 신호만을 사용하여 위치를 결정하며, "Column 3, Lines 15-40: The positioning module processes the received signal data using a Kalman filter algorithm to produce a smoothed location estimate."와 같이 무선 신호 자체를 처리하여 위치를 추정하는 것을 개시합니다. D1은 관성 센서 데이터(inertial sensor data)와의 융합(fusing)에 대해 전혀 언급하지 않습니다. (D1 NOTE: "This prior art document does NOT disclose: ... Fusion with inertial sensor (IMU) data")
        *   **인용발명 D2:** D2는 이종 무선 신호(RSSI, RTT)를 결합하여 위치 측정 지표를 계산하고 이를 위치 추정 모듈에 제공하는 것을 개시합니다. "Paragraph [0030]-[0040]: The invention uses a two-step process: (1) individual signal type processing and (2) metric fusion. Each signal type is processed independently to produce a preliminary position estimate, then these estimates are combined using a fixed fusion algorithm."에서 "metric fusion"은 서로 다른 무선 신호 유형으로부터 얻은 추정치를 결합하는 것을 의미하며, 관성 센서 데이터와의 융합은 아닙니다. (D2 NOTE: "This prior art document does NOT disclose: ... Integration with inertial sensor data")
        *   **결론:** 본원발명 (C)의 "fusing the first positioning reference value with inertial sensor data" 구성은 인용발명 D1 및 D2에 명확히 개시되어 있지 않은 차이점입니다.

### 2. 기능적/효과적 차이점 특정

본원발명 청구항 1의 구성요소 (C)인 "determining a position by fusing the first positioning reference value with inertial sensor data"는 인용발명 D1 및 D2에 개시된 기술과 비교하여 다음과 같은 명확한 기능적/효과적 차이를 가집니다.

*   **기술적 기능 및 효과의 차이:**
    *   인용발명 D1과 D2는 모두 무선 신호 기반 측위의 정확도 향상에 초점을 맞추고 있습니다. 무선 신호 기반 측위는 실내 환경에서 신호 음영 지역, 다중 경로 오차, AP 지문 정보 변화 등에 취약하여 정확도와 안정성이 저하될 수 있는 본질적인 한계를 가집니다.
    *   본원발명은 이러한 무선 신호 기반 측위의 한계를 극복하기 위해, 무선 신호로부터 산출된 제1 측위 기준값과 관성 센서(inertial sensor) 데이터를 '융합(fusing)'하여 최종 위치를 결정합니다. 관성 센서 기반 측위(예: PDR)는 단기적으로는 정밀한 상대적 이동 정보를 제공하지만, 시간이 지남에 따라 드리프트 오차가 누적되는 단점이 있습니다.
    *   본원발명의 융합 기술은 무선 신호 기반 측위의 광역적인 위치 정보와 관성 센서 기반 측위의 정밀한 상대적 이동 정보를 상호 보완적으로 활용함으로써, 각 시스템의 고유한 단점을 극복하고 전반적인 측위 정확도와 안정성을 크게 향상시키는 기능을 제공합니다.
*   **명세서 근거:**
    *   "무선 신호 기반 측위의 단점(예: 신호 음영 지역, 다중 경로 오차)과 관성 센서 기반 측위의 단점(예: 드리프트 오차 누적)을 상호 보완합니다." (spec [0004])
    *   "이를 통해 실내 환경 등에서 종래 기술 대비 50% 이상 측위 오차를 줄이는 현저한 효과(spec [0005])를 달성하여, 보다 정확하고 안정적인 위치 측정이 가능하게 합니다." (spec [0004])

### 3. 예측하지 못한 현저한 효과(Unexpected Remarkable Effect) 검토

본원발명은 인용발명 D1 및 D2로부터 예측할 수 없었던 현저한 효과를 달성합니다.

*   **검토 결과:** 본원발명은 무선 신호 기반 측위와 관성 센서 데이터 융합을 통해 종래 기술 대비 50% 이상의 측위 오차 감소라는 예측 불가한 현저한 효과를 달성합니다.
*   **구체적 근거:** 명세서 [0005]에 따르면, "본 발명에 따르면, 종래 기술 대비 실내 측위 오차를 50% 이상 줄일 수 있는 현저한 효과가 있다."
*   **설명:** 인용발명 D1과 D2는 각각 무선 신호 기반 측위의 정확도 향상에 기여하는 기술을 개시하지만, 관성 센서 데이터와의 융합을 통한 측위 오차 감소에 대해서는 전혀 언급하지 않습니다. 특히, 50% 이상의 측위 오차 감소는 단순히 두 기술을 결합했을 때 예상할 수 있는 단순한 합산 효과를 넘어선, 예측 불가한 시너지 효과로 볼 수 있습니다. 이는 무선 신호의 불안정성과 관성 센서의 드리프트 오차라는 각 기술의 근본적인 한계를 동시에 해결함으로써 달성되는 결과이며, 인용발명들이 제시하는 문제 의식이나 해결 방안으로는 도저히 예측할 수 없는 효과입니다.

### 4. 심사관 논거의 약점 파악

심사관은 본원발명의 청구항 1이 인용발명 D1 또는 D2에 공지된 관성 센서 데이터 융합 기술을 결합함으로써 용이하게 도출될 수 있다고 주장할 가능성이 있습니다. 이러한 심사관 논거의 약점은 다음과 같습니다.

1.  **논리적 비약 및 사후적 고찰 (Hindsight):** 심사관은 본원발명의 내용을 알고 난 후에야 D1/D2에 관성 센서 융합 기술을 결합할 동기가 있다고 주장할 수 있습니다. 그러나 D1과 D2는 모두 무선 신호 기반 측위에 초점을 맞추고 있으며, 관성 센서 데이터 융합의 필요성이나 동기를 전혀 제시하지 않습니다. 특히 D1과 D2 모두 "Fusion with inertial sensor (IMU) data" 또는 "Integration with inertial sensor data"를 개시하지 않는다고 명시적으로 언급되어 있습니다. 이는 심사관이 본원발명의 발명을 사후적으로 분석하여 인용문헌을 조합하려는 전형적인 시도로 볼 수 있습니다.
2.  **과도한 일반화:** 심사관은 "위치 측정 기술 분야에서 무선 신호와 관성 센서 데이터 융합은 공지된 기술이다"라고 주장할 수 있습니다. 그러나 본원발명은 단순히 융합하는 것을 넘어, '제1 측위 기준값'이라는 특정 형태의 무선 신호 처리 결과와 관성 센서 데이터를 융합하는 구체적인 방법을 제시합니다. 단순히 "공지된 융합"이라고 주장하는 것은 본원발명의 구체적인 기술적 기여와 그로 인한 현저한 효과를 간과하는 것입니다.
3.  **결합 동기 부재:** D1과 D2는 각각 무선 신호 기반 측위의 정확도를 높이는 데 주력하고 있으며, 관성 센서의 드리프트 오차 문제를 해결하거나 무선 신호의 한계를 보완하기 위해 관성 센서 데이터를 융합해야 한다는 어떠한 '가르침(Teaching)', '암시(Suggestion)', 또는 '동기(Motivation)'도 제공하지 않습니다. 두 기술 분야는 서로 다른 문제점을 해결하려는 독립적인 접근 방식을 가지고 있습니다.

### 5. 인용문헌 결합 동기(TSM: Teaching, Suggestion, Motivation) 분석

*   **D1, D2를 결합하려는 동기가 인용문헌들에 명시적으로 존재하는가?**
    *   **아니오.** 인용문헌 D1은 무선 신호(RSSI)를 기반으로 위치 기준값을 계산하고 칼만 필터로 평활화하여 위치를 추정하는 데 중점을 둡니다. 인용문헌 D2는 이종 무선 신호(RSSI, RTT)를 수집하고 이를 결합하여 복합 기준값을 생성하는 데 중점을 둡니다. 두 인용문헌 모두 '관성 센서 데이터'를 활용하여 측위 정확도를 높여야 한다는 어떠한 가르침, 암시, 또는 동기도 제공하지 않습니다. 오히려 D1과 D2 모두 관성 센서 데이터와의 융합을 개시하지 않는다고 명시적으로 언급되어 있습니다. 각 인용문헌은 자신의 기술 분야 내에서 특정 문제(예: 무선 신호 기반 측위의 정확도 향상)를 해결하려는 독립적인 시도를 하고 있을 뿐, 다른 기술 분야(관성 센서 융합)와의 결합을 제안하지 않습니다.

*   **결합 시 예측 가능한 결과인가, 아니면 예측 불가한 시너지 효과가 있는가?**
    *   **예측 불가한 시너지 효과가 있습니다.** 단순히 무선 신호 기반 측위와 관성 센서 기반 측위 기술을 결합하는 것이 공지된 개념일 수 있지만, 본원발명에서 제시하는 "종래 기술 대비 실내 측위 오차를 50% 이상 줄일 수 있는 현저한 효과(spec [0005])"는 단순한 기술의 병렬적 결합으로 예상할 수 있는 결과를 넘어선다. 무선 신호의 불안정성과 관성 센서의 드리프트 오차라는 각 기술의 고유한 한계를 상호 보완적으로 해결함으로써, 개별 기술로는 달성하기 어려운 높은 수준의 정확도와 안정성을 제공합니다. 이러한 현저한 효과는 결합의 동기가 없었을 뿐만 아니라, 결합 결과 또한 예측하기 어려웠음을 시사합니다.

*   **심사관이 결합을 제안한 근거의 타당성을 검토하라.**
    *   **타당하지 않습니다.** 심사관이 D1 또는 D2에 공지된 관성 센서 융합 기술을 결합하여 본원발명이 용이하게 도출된다고 주장한다면, 이는 다음과 같은 이유로 타당성이 부족합니다.
        1.  **결합 동기 부재:** D1과 D2는 관성 센서 데이터와의 융합을 통해 측위 정확도를 향상시켜야 한다는 어떠한 동기도 제공하지 않습니다. 이들은 각기 다른 방식으로 무선 신호 기반 측위의 한계를 극복하려 할 뿐입니다.
        2.  **문제 의식의 차이:** D1과 D2는 무선 신호의 불안정성, 다중 경로, AP 지문 변화 등의 문제에 초점을 맞추는 반면, 본원발명은 이러한 문제와 더불어 관성 센서의 드리프트 오차 문제를 동시에 해결하려는 새로운 문제 의식을 가지고 있습니다.
        3.  **사후적 고찰 (Hindsight):** 본원발명의 발명을 알고 난 후에야 인용문헌에 관성 센서 융합 기술을 결합하는 것이 용이하다고 주장하는 것은 전형적인 사후적 고찰에 해당합니다. 발명 당시의 기술 수준에서 인용문헌만으로는 이러한 결합을 시도할 동기가 없었습니다.
        4.  **예측 불가한 효과:** 앞서 언급했듯이, 본원발명은 50% 이상의 측위 오차 감소라는 예측 불가한 현저한 효과를 달성합니다. 이는 단순히 공지 기술의 결합으로 얻을 수 있는 결과가 아닙니다.