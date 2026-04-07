## 의견제출통지서 대응 전략 수립

### A) 보정 전략 (Amendment)

**1. 청구항 1 (톤 맵핑 거리(DTM)를 이용한 인접 톤의 비-인접 톤 맵핑 및 송신)**

*   **제안 보정 내용:**
    *   `mapping the set of contiguous tones of the selected RU to a set of non-contiguous tones distributed across the frequency spectrum using a tone mapping distance (DTM) applicable to an entirety of the frequency spectrum` 부분을 다음과 같이 한정하여, `DTM`이 전체 주파수 스펙트럼에 걸쳐 일관되게 적용되는 *글로벌 파라미터*로서 기능하며, 그 목적이 전체 시스템의 `PSD` 제한 완화 및 송신 전력 최적화에 있음을 명확히 할 수 있습니다.
    *   **예시 보정안:** `mapping the set of contiguous tones of the selected RU to a set of non-contiguous tones distributed across the frequency spectrum using a single, globally applied tone mapping distance (DTM) parameter applicable to an entirety of the frequency spectrum for optimizing overall power spectral density (PSD) limits and maximizing total transmit power.`
*   **권리범위 축소 리스크 평가:**
    *   `single, globally applied DTM parameter` 및 `optimizing overall PSD limits and maximizing total transmit power`와 같은 문구를 추가함으로써, `DTM`의 적용 방식 및 목적이 더욱 구체화되어 권리범위가 다소 축소될 수 있습니다. 그러나 이는 본원발명의 핵심적인 발명적 특징을 명확히 하는 것이므로, 불필요한 축소라기보다는 발명의 진정한 가치를 반영하는 것으로 볼 수 있습니다.
*   **보정 후 기대 효과:**
    *   심사관이 D1, D2의 `DTM` 개념과 본원발명의 `DTM` 개념 간의 차이점을 보다 명확하게 인식하도록 도울 수 있습니다. 특히, 인용문헌들이 개별 `RU` 단위의 맵핑을 설명하는 것과 달리, 본원발명이 `entirety of the frequency spectrum`에 대한 `글로벌 DTM` 적용을 통해 시스템 전체의 성능을 최적화하는 점을 부각할 수 있습니다.

**2. 청구항 21 (파싱(parsing)을 이용한 인접 톤의 비-인접 톤 변환 및 송신 스케줄링)**

*   **제안 보정 내용:**
    *   `parsing the plurality of contiguous tones of the selected RU to one or more sets of non-contiguous tones associated with a tone mapping number, wherein each set of non-contiguous tones spans a unique frequency segment of a second frequency bandwidth that is wider than the first frequency bandwidth` 부분을 다음과 같이 한정하여, `parsing`의 구체적인 목적 및 `unique frequency segment` 할당의 기술적 의의를 강조할 수 있습니다.
    *   **예시 보정안:** `parsing the plurality of contiguous tones of the selected RU into one or more sets of non-contiguous tones associated with a tone mapping number, wherein each set of non-contiguous tones is specifically allocated to span a unique frequency segment of a second frequency bandwidth that is wider than the first frequency bandwidth, thereby enabling hierarchical tone distribution for enhanced PSD management and flexible resource utilization.`
*   **권리범위 축소 리스크 평가:**
    *   `specifically allocated` 및 `thereby enabling hierarchical tone distribution for enhanced PSD management and flexible resource utilization`와 같은 문구를 추가함으로써, `parsing` 및 `unique frequency segment` 할당의 목적과 효과가 명확해지므로 권리범위가 다소 구체화될 수 있습니다. 이는 발명의 기술적 특징을 더욱 명확히 하는 방향이므로, 심사관의 이해를 돕는 데 효과적일 것입니다.
*   **보정 후 기대 효과:**
    *   심사관이 D1, D2의 단순한 `mapping` 개념과 본원발명의 `parsing` 개념 간의 차이, 그리고 `unique frequency segment` 할당의 구조적 특징을 명확히 인지하도록 도울 수 있습니다. 특히, `PSD` 관리 및 유연한 자원 활용이라는 예측 불가한 효과를 보정 내용에 포함하여 진보성 주장의 근거를 강화할 수 있습니다.

**3. 청구항 34 (트리거 프레임 기반 UL 송신을 위한 글로벌 DTM 맵핑)**

*   **제안 보정 내용:**
    *   `mapping the set of contiguous tones of the first RU to a first set of non-contiguous tones distributed across the first frequency spectrum based on a tone mapping distance (DTM) applicable to each RU of the group of RUs` 부분을 다음과 같이 한정하여, `UL` 환경에서 `RU` 그룹 전체에 걸쳐 일관되게 적용되는 `DTM`의 `글로벌` 특성 및 그 목적을 강조할 수 있습니다.
    *   **예시 보정안:** `mapping the set of contiguous tones of the first RU to a first set of non-contiguous tones distributed across the first frequency spectrum based on a single, consistent tone mapping distance (DTM) parameter globally applicable to each RU of the group of RUs for optimizing uplink (UL) transmit power and system capacity in a multi-user environment.`
*   **권리범위 축소 리스크 평가:**
    *   `single, consistent DTM parameter globally applicable` 및 `optimizing UL transmit power and system capacity in a multi-user environment`와 같은 문구를 추가함으로써, `DTM`의 적용 방식 및 `UL` 환경에서의 목적이 더욱 구체화되어 권리범위가 다소 축소될 수 있습니다. 그러나 이는 `UL` 다중 사용자 환경에서의 본원발명의 핵심적인 발명적 특징을 명확히 하는 것이므로, 심사관의 이해를 돕는 데 효과적일 것입니다.
*   **보정 후 기대 효과:**
    *   심사관이 D1, D2의 일반적인 `DTM` 개념과 본원발명의 `UL` 다중 사용자 환경에서의 `RU` 그룹에 대한 `글로벌 DTM` 적용 간의 차이점을 명확히 인식하도록 도울 수 있습니다. 특히, `UL` 송신 전력 최적화 및 시스템 용량 증대라는 예측 불가한 효과를 보정 내용에 포함하여 진보성 주장의 근거를 강화할 수 있습니다.

---

### B) 의견서 전략 (Written Opinion)

**1. 핵심 주장 구성:**
*   **구조적 차이점 강조:** 각 청구항별로 인용문헌에 명시적으로 개시되지 않은 구조적 차이점(예: 청구항 1의 "entirety of the frequency spectrum"에 적용 가능한 `글로벌 DTM`, 청구항 21의 "parsing" 및 "unique frequency segment", 청구항 34의 `UL` 다중 사용자 환경에서의 `RU` 그룹에 대한 `글로벌 DTM` 적용)을 명확히 제시합니다.
*   **결합 동기 부재:** 인용문헌 D1과 D2는 각각의 기술적 특징을 개시하지만, 심사관이 주장하는 방식으로 이들을 결합하여 본원발명의 차이 구성에 도달할 어떠한 가르침, 시사 또는 동기를 제공하지 않음을 강력히 주장합니다. 특히, D1과 D2의 `DTM` 개념은 개별 `RU` 단위의 맵핑에 초점을 맞추고 있으며, 본원발명과 같이 `전체 주파수 스펙트럼` 또는 `RU 그룹`에 걸쳐 `글로벌`하게 적용되는 `DTM`의 개념이나 `parsing`과 같은 복합적인 톤 변환 및 할당 방식은 인용문헌에서 유추하기 어렵습니다.
*   **예측 불가한 현저한 효과:** 본원발명의 차이 구성이 단순히 인용문헌의 결합으로 얻을 수 있는 통상의 기술적 효과를 넘어, 예측 불가한 현저한 효과를 제공함을 구체적으로 설명합니다.
    *   **청구항 1:** `글로벌 DTM`을 통해 전체 스펙트럼 관점에서 `PSD` 제한을 효율적으로 완화하고 총 송신 전력을 극대화하여 시스템 성능을 향상시키는 효과.
    *   **청구항 21:** `parsing` 및 `unique frequency segment` 할당을 통한 다단계적이고 계층적인 톤 분산 방식이 `PSD` 제한을 더욱 효율적으로 관리하고, 다중 사용자 환경에서 간섭을 최소화하며, 유연한 자원 활용을 가능하게 하는 효과.
    *   **청구항 34:** `UL` 다중 사용자 환경에서 `trigger frame`을 통해 할당된 `RU` 그룹에 대해 `글로벌 DTM`을 적용하여 `UL` 송신 전력을 효율적으로 증가시키고, `UL` 송신의 신뢰성, 효율성 및 시스템 용량을 향상시키는 효과.

**2. 심사관 논거 약점에 대한 반박 포인트:**
*   **사후적 고찰(Hindsight) 반박:** 심사관의 결합 논리가 본원발명의 발명적 특징을 사후적으로 고찰한 것임을 지적합니다. 인용문헌들은 본원발명의 특정 문제 해결 방식(예: `글로벌 DTM`의 적용 범위, `parsing`의 복잡성, `UL` 다중 사용자 환경에서의 `RU` 그룹 최적화)에 대한 어떠한 동기나 시사를 제공하지 않습니다.
*   **일반적인 개념과 구체적인 구현의 차이:** 심사관이 인용문헌의 일반적인 `distributed RUs` 개념이나 `DTM` 개념을 본원발명의 구체적이고 구조화된 특징(예: `entirety of the frequency spectrum`에 대한 `DTM` 적용, `parsing`을 통한 `unique frequency segment` 할당, `RU` 그룹에 대한 `글로벌 DTM` 적용)과 동일시하는 오류를 지적합니다. 일반적인 개념만으로는 본원발명의 특정 기술적 해결책에 도달할 수 없습니다.
*   **D2의 `DTM` 관련 언급 반박 (청구항 1 관련):** D2 [0143]의 "minimum mapping distance... may depend on the logic RU size for the channel bandwidth"는 `DTM` 값이 `RU` 크기에 따라 달라질 수 있음을 시사하여, 오히려 `DTM`이 `entirety of the frequency spectrum`에 대해 *단일하게 적용되는 것이 아닐 수 있음*을 암시하므로, 심사관의 `글로벌 DTM` 도출 논거를 약화시키는 근거로 활용합니다.
*   **거절이유 1 (1군의 발명) 반박 (청구항 21, 34 관련):** 청구항 21 및 34가 `PPDU`가 주파수 상에서 `non-contiguous tones`의 세트로 송수신되는 공통된 기술적 특징을 가지며, 이는 인용발명 1의 일반적인 `distributed RUs` 개념에 비해 개선된 것이 아니라는 심사관의 주장은 타당하지 않음을 주장합니다. 각 발명은 `non-contiguous tones`를 생성하고 활용하는 방식에 있어 `parsing` 또는 `UL` 다중 사용자 환경에서의 `글로벌 DTM`과 같은 고유한 기술적 특징을 가지며, 이는 인용문헌의 일반적인 개념을 넘어서는 발명적 진보를 포함합니다. 따라서 각 발명은 독립적인 발명적 특징을 가지며, 하나의 총괄적 발명의 개념을 형성하는 1군의 발명으로 볼 수 있습니다. (다만, 이 부분은 진보성 거절이유와는 별개로 1군의 발명 요건에 대한 반박이므로, 진보성 논의와 분리하여 처리합니다.)

---

### C) 보정 + 의견서 병행 전략

이 전략은 가장 강력하고 효과적인 대응 방안입니다.

*   **보정의 역할:**
    *   청구항의 문구를 수정하여 본원발명의 핵심적인 발명적 특징과 인용문헌과의 차이점을 더욱 명확하고 간결하게 제시합니다. 이는 심사관이 청구항을 읽었을 때 발명의 진보성을 직관적으로 이해할 수 있도록 돕습니다.
    *   특히, `글로벌 DTM`, `parsing`의 구체적인 목적, `UL` 다중 사용자 환경에서의 `RU` 그룹 최적화 등 본원발명의 고유한 개념을 청구항에 직접 반영하여, 심사관이 인용문헌과 본원발명의 기술적 차이를 명확히 구분하도록 유도합니다.
    *   불필요한 모호성을 제거하여 심사관의 오해를 줄이고, 의견서의 주장을 뒷받침하는 법적 근거를 강화합니다.

*   **의견서의 역할:**
    *   보정된 청구항을 기반으로, Step 3에서 도출된 상세한 기술적 논거를 제시하여 심사관의 거절이유를 반박합니다.
    *   인용문헌에 본원발명의 차이 구성에 대한 결합 동기가 전혀 없음을 논리적으로 설명하고, 심사관의 결합 논리가 사후적 고찰에 불과함을 강조합니다.
    *   본원발명의 차이 구성이 제공하는 예측 불가한 현저한 효과를 구체적인 기술적 근거와 함께 제시하여, 발명의 진보성을 강력하게 주장합니다.
    *   보정된 청구항의 문구가 의미하는 바를 상세히 설명하고, 해당 문구가 인용문헌의 기술과 어떻게 차별화되는지를 명확히 합니다.

---

### 권고안

**가장 권고하는 전략은 C) 보정 + 의견서 병행 전략입니다.**

**이유:**

1.  **명확성 및 설득력 극대화:** 보정을 통해 청구항의 발명적 특징을 명확히 하고, 의견서를 통해 그 특징이 왜 진보적인지를 상세히 설명함으로써, 심사관에게 본원발명의 진보성을 가장 효과적으로 전달할 수 있습니다. 청구항 문구의 모호성으로 인한 심사관의 오해를 줄이고, 의견서의 기술적 주장에 힘을 실어줄 수 있습니다.
2.  **리스크 최소화:** 의견서만 제출할 경우, 심사관이 청구항 문구 자체에서 발명적 특징을 충분히 인지하지 못하면 의견서의 설득력이 떨어질 수 있습니다. 반대로 보정만 할 경우, 보정된 청구항이 여전히 심사관에게 자명하게 느껴질 수 있으며, 보정으로 인한 권리범위 축소의 위험만 커질 수 있습니다. 보정과 의견서를 병행함으로써 이러한 단점들을 상호 보완하여 리스크를 최소화할 수 있습니다.
3.  **심사관의 이해 증진:** 심사관은 제한된 시간 내에 많은 사건을 처리하므로, 보정을 통해 청구항의 핵심을 명확히 제시하는 것이 심사관의 이해를 돕는 데 매우 중요합니다. 이후 의견서에서 상세한 기술적 배경과 진보성 논거를 제시하여 심사관의 판단을 유도하는 것이 효과적입니다.

**리스크와 기대 성공 가능성:**

*   **리스크:** 보정으로 인한 권리범위 축소는 불가피하지만, 본원발명의 핵심적인 발명적 특징을 명확히 하는 방향으로 이루어지므로 과도한 축소는 아닐 것입니다. 또한, 심사관이 여전히 인용문헌의 결합이 자명하다고 판단할 가능성은 항상 존재합니다.
*   **기대 성공 가능성:** Step 3에서 도출된 진보성 논거(특히, 결합 동기 부재 및 예측 불가한 현저한 효과)는 매우 강력합니다. 이 논거들을 보정된 청구항과 결합하여 체계적으로 제시한다면, 심사관이 거절이유를 철회하고 특허를 허여할 가능성이 높습니다. 특히, `글로벌 DTM`, `parsing` 및 `unique frequency segment` 할당, `UL` 다중 사용자 환경에서의 `RU` 그룹 최적화 등은 인용문헌에서 직접적으로 가르치거나 시사하지 않는 구체적인 기술적 해결책이므로, 진보성 인정 가능성이 높다고 판단됩니다.

이 전략은 변리사님의 최종 검토를 거쳐 확정될 예정입니다.