## 한국 특허 전문가 분석: 단일성 위반 거절이유 (특허법 제45조) 전략 수립

### 1. 심사관의 단일성 위반 거절이유 요약

심사관은 청구항 그룹 A (1~5항, 위치측정 방법)와 그룹 B (6~8항, 단말 장치)가 인용발명 D1에 비하여 개선된 공통의 특별한 기술적 특징(STF)을 공유하지 않으므로 단일성 요건(특허법 제45조)을 만족하지 않는다고 판단하였습니다. D1은 이미 위치 측정 방법과 이를 구현하는 단말 장치 모두를 개시하고 있다는 점을 근거로 들고 있습니다.

### 2. Step 2 분석 결과 요약 (잠재적 STF)

Step 2 분석 결과, 청구항 1 (방법)과 청구항 6 (장치)의 공통 구성 중 "제1 측위 기준값 산출" 부분이 D1 대비 개선된 STF를 포함할 가능성이 높습니다.
*   **STF 후보:** "RSSI, RTT, AoA를 동시에 결합한 가중 평균으로 산출되는 제1 측위 기준값" (A first positioning reference value calculated as a weighted average combining RSSI, RTT, and AoA simultaneously).
*   **D1 대비 개선점:** D1은 RSSI만을 이용한 거리 추정치의 가중 평균을 개시하며, RTT 및 AoA와 같은 다른 무선 신호 지표를 동시에 결합하는 다중 지표 융합을 개시하지 않습니다. 이는 측위 정확도를 향상시키는 개선된 기술적 특징입니다.
*   **문제점:** 이 STF는 명세서 [0002] 및 종속항 3에 의해 뒷받침되지만, 독립항 1과 6 자체에는 명시적으로 기재되어 있지 않아 심사관이 공통 STF로 인정하지 않을 여지가 있습니다.

---

### A) 일부 그룹 삭제 (Deletion of Claims)

*   **삭제할 그룹:** 본 발명의 핵심 기술이 방법과 장치 모두에 걸쳐 있으므로, 어느 한 그룹을 삭제하는 것은 권리범위의 상당한 손실을 초래합니다. 예를 들어, 그룹 A(방법)를 삭제하거나 그룹 B(장치)를 삭제할 수 있습니다.
*   **권리범위 손실 및 보호 가치 평가:** 양 그룹 모두 발명의 중요한 측면을 보호하므로, 어느 한 그룹을 삭제할 경우 발명의 보호 범위가 크게 축소됩니다. 이는 바람직하지 않은 선택입니다.
*   **분할출원 필요성:** 삭제된 그룹에 대해서는 분할출원을 통해 별도로 권리를 확보해야 합니다.
*   **리스크:** 핵심 발명의 보호 범위가 축소되고, 분할출원 시 추가 비용과 절차적 부담이 발생합니다.
*   **장점:** 현재 출원의 심사 부담을 줄여 빠르게 등록받을 수 있습니다.

---

### B) 보정 없이 단일성 주장 (Assert Unity Without Amendment)

*   **주장 가능한 논거:**
    1.  **공통 STF 존재:** 청구항 1의 "제1 측위 기준값을 산출하는 단계"와 청구항 6의 "제1 측위 기준값 산출부"는 명세서 [0002]에 따라 "RSSI, RTT, AoA를 동시에 결합한 가중 평균으로 산출되는 제1 측위 기준값"을 의미합니다. 이는 D1이 개시하지 않는 다중 신호 지표 융합을 통한 측위 정확도 향상이라는 개선된 기술적 특징(STF)을 공유합니다.
    2.  **D1 대비 개선점:** D1 (Column 5, Lines 10-30)은 RSSI만을 이용한 거리 추정치의 가중 평균을 개시하며, RTT 및 AoA를 동시에 결합하는 다중 지표 융합을 개시하지 않습니다. D1의 한계점(Paragraphs [0045]-[0052])은 고정된 가중치 방식을 언급하며, 본 발명의 동적 조정 및 다중 지표 융합과는 차이가 있습니다.
    3.  **대응되는 STF:** 청구항 그룹 A(방법)는 해당 STF를 수행하는 단계를, 그룹 B(장치)는 해당 STF를 수행하도록 구성된 수단을 청구하므로, 양 그룹은 D1 대비 개선된 STF를 대응되는 형태로 공유합니다.
*   **심사관 논거의 약점 및 반박 포인트:**
    *   **심사관:** "D1 대비 개선된 공통 STF 부재."
    *   **반박:** 독립항의 "제1 측위 기준값"은 명세서에 의해 정의된 특정 기술적 특징(RSSI, RTT, AoA 동시 결합 가중 평균)을 내포하며, 이는 D1 대비 명확히 개선된 STF입니다.
    *   **심사관:** "D1은 방법과 장치 모두 개시."
    *   **반박:** D1이 방법과 장치 모두를 개시하더라도, 본 출원의 STF는 D1이 개시하지 않는 *개선된* 기술적 특징이므로 단일성 판단에 영향을 미치지 않습니다.
*   **성공 가능성:** 보통.
    *   **근거:** STF 자체는 D1 대비 개선되었으나, 해당 STF가 독립항 자체에 명시적으로 기재되어 있지 않고 명세서의 정의에 의존해야 하므로, 심사관이 독립항의 범위를 넓게 해석하여 STF 공유를 인정하지 않을 가능성이 있습니다.

---

### C) 독립항 보정 후 단일성 주장 (Amend Independent Claims, Then Argue)

*   **보정 방향:** 청구항 1과 청구항 6의 독립항에 Step 2에서 확인된 STF를 명시적으로 추가하여, 양 독립항이 D1 대비 개선된 공통 STF를 공유함을 명확히 합니다.
*   **추가할 한정 사항:** "wherein the first positioning reference value is calculated as a weighted average combining RSSI, RTT, and AoA simultaneously."
*   **보정 예시 방향 (영문 클레임 언어):**
    *   **Amended Claim 1:** A method for measuring a position, comprising:
        collecting a plurality of wireless signals;
        calculating a first positioning reference value based on the collected wireless signals, **wherein the first positioning reference value is calculated as a weighted average combining RSSI, RTT, and AoA simultaneously**; and
        determining a position by fusing the first positioning reference value with inertial sensor data.
    *   **Amended Claim 6:** A terminal device comprising:
        a wireless signal collector configured to collect a plurality of wireless signals;
        a first positioning reference value calculator configured to calculate a first positioning reference value, **wherein the first positioning reference value calculator is configured to calculate the first positioning reference value as a weighted average combining RSSI, RTT, and AoA simultaneously**; and
        a position determiner configured to determine a position based on the first positioning reference value.
*   **보정 후 단일성 주장 논거:** 보정된 청구항 1과 6은 모두 "RSSI, RTT, AoA를 동시에 결합한 가중 평균으로 산출되는 제1 측위 기준값"이라는 D1 대비 개선된 공통 STF를 명시적으로 포함하므로, 발명의 단일성 요건을 만족합니다.
*   **권리범위 축소 여부:** 독립항의 범위가 축소되지만, 이는 본 발명의 핵심적인 진보적 특징을 명확히 함으로써 거절이유를 해소하고 등록 가능성을 높이는 효과적인 방법입니다. 축소된 범위 내에서 핵심 발명을 보호할 수 있습니다.

---

### D) 분할출원 (Divisional Application)

*   **분리할 그룹 제안:** 현재 출원에는 그룹 A(방법)를 남기고, 그룹 B(장치)를 분할출원으로 분리하거나 그 반대로 진행할 수 있습니다.
*   **분할 시 유의사항:**
    *   **시기:** 원출원에 대한 최종 거절결정 등본 송달일로부터 30일 이내 또는 심사관의 최초 거절이유통지서에 대한 의견서 제출기간 이내에 제출하는 것이 일반적입니다.
    *   **원출원과의 권리관계:** 분할출원은 원출원의 출원일을 소급 적용받아 신규성 및 진보성 판단에 유리합니다.
    *   **비용:** 분할출원 시 별도의 출원료 및 심사료가 발생하며, 별도의 심사 절차를 거쳐야 합니다.
*   **평가:** 단일성 거절이유를 해소하는 한 가지 방법이지만, 추가 비용과 절차가 수반됩니다. 보정을 통해 단일성을 확보할 수 있다면, 분할출원은 차선책으로 고려될 수 있습니다.

---

### [최종 확정 전략]

**확정 전략:** **C) 독립항 보정 후 단일성 주장 (Amend Independent Claims, Then Argue)**

**선택 이유:**
Step 2 분석 결과, D1 대비 개선된 명확한 STF("RSSI, RTT, AoA를 동시에 결합한 가중 평균으로 산출되는 제1 측위 기준값")가 존재함을 확인했습니다. 그러나 이 STF가 독립항 자체에 명시적으로 기재되어 있지 않아 심사관이 단일성을 인정하지 않을 가능성이 있습니다.

옵션 B(보정 없이 주장)는 심사관의 해석에 따라 성공 가능성이 보통 수준에 머물 수 있습니다. 반면, 옵션 C(독립항 보정)는 이 STF를 독립항 1과 6에 명시적으로 포함시킴으로써, 양 그룹이 D1 대비 개선된 공통 STF를 공유한다는 점을 명확히 입증할 수 있습니다. 이는 심사관의 거절이유를 직접적으로 해소하고 등록 가능성을 가장 높이는 효과적인 방법입니다. 비록 권리범위가 다소 축소될 수 있으나, 본 발명의 핵심적인 진보적 특징을 보호하면서 안정적으로 특허를 확보하는 데 유리합니다.

**확정된 전략에 따른 Step 4(영문 코멘트 작성) 핵심 논거 및 보정 방향 요약:**

1.  **심사관 의견 이해:** 심사관이 청구항 그룹 A(방법)와 그룹 B(장치) 간에 D1 대비 개선된 공통 STF가 없다고 판단했음을 인정합니다.
2.  **STF 식별 및 D1 대비 개선점 강조:**
    *   본 발명의 STF는 "RSSI, RTT, AoA를 동시에 결합한 가중 평균으로 산출되는 제1 측위 기준값"입니다.
    *   D1 (Column 5, Lines 10-30)은 RSSI만을 이용한 가중 평균을 개시하며, 다중 신호 지표(RTT, AoA)를 동시에 결합하는 기술은 개시하지 않습니다. 이는 D1의 한계점(Paragraphs [0045]-[0052])과 대비되어 본 발명의 STF가 D1 대비 현저히 개선된 기술적 특징임을 강조합니다.
3.  **독립항 보정 제안:**
    *   청구항 1 (방법)과 청구항 6 (장치)의 독립항에 상기 STF를 명시적으로 추가하는 보정을 제안합니다.
    *   **청구항 1 보정 방향:** "calculating a first positioning reference value... **wherein the first positioning reference value is calculated as a weighted average combining RSSI, RTT, and AoA simultaneously**."
    *   **청구항 6 보정 방향:** "a first positioning reference value calculator configured to calculate a first positioning reference value, **wherein the first positioning reference value calculator is configured to calculate the first positioning reference value as a weighted average combining RSSI, RTT, and AoA simultaneously**."
4.  **보정 후 단일성 주장:** 보정된 독립항 1과 6은 D1 대비 개선된 공통 STF를 명확히 공유하므로, 특허법 제45조의 단일성 요건을 만족함을 주장합니다.
5.  **권리범위 축소에 대한 언급:** 보정으로 인한 권리범위 축소는 인정하지만, 이는 핵심 발명의 보호를 확보하고 거절이유를 효과적으로 해소하기 위한 전략적 선택임을 설명합니다.