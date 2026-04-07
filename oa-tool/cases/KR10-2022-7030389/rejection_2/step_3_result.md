## Step 3: 심사관 지적 타당성 분석

### 대표 독립항: 청구항 1 (톤 맵핑 거리(DTM)를 이용한 인접 톤의 비-인접 톤 맵핑 및 송신)

**1. 심사관 지적 요약:**
심사관은 청구항 1의 구성 중 `selecting a resource unit (RU)` 및 `transmitting the PPDU`는 인용발명 1(D1)에 개시되어 동일하다고 판단하였습니다. `mapping the set of contiguous tones of the selected RU to a set of non-contiguous tones distributed across the frequency spectrum using a tone mapping distance (DTM)` 구성에 대해서는 D1이 DTM을 사용하여 인접 톤을 주파수 스펙트럼에 걸쳐 분산된 비-인접 톤 세트에 맵핑하는 것을 개시하지만, "주파수 스펙트럼 전체에 적용 가능한 DTM (DTM applicable to an entirety of the frequency spectrum)"이라는 점이 명시적으로 없다는 차이점을 지적했습니다. 그러나 심사관은 이 차이 구성이 인용발명 2(D2)의 "분산 매핑을 위해 주파수 스펙트럼 또는 채널 대역폭 전체에 적용 가능한 톤 매핑 거리를 사용하는 점"을 D1에 결합함으로써 쉽게 도출될 수 있으므로, 청구항 1은 D1, D2의 결합에 의해 진보성이 없다고 판단했습니다.

**2. 심사관 지적 타당성 분석:**

*   **구성 1 (`selecting a resource unit (RU)`) 및 구성 3 (`transmitting the PPDU`):**
    *   심사관의 지적은 타당합니다. D1은 `PPDU` 송수신을 위한 `RU` 할당(선택) 및 `PPDU` 송신을 개시합니다 (D1 [0057]-[0062], [0105]-[0109], [0060]).

*   **구성 2 (`mapping the set of contiguous tones of the selected RU to a set of non-contiguous tones distributed across the frequency spectrum using a tone mapping distance (DTM) applicable to an entirety of the frequency spectrum`):**
    *   **차이점:** "DTM applicable to an entirety of the frequency spectrum" (주파수 스펙트럼 전체에 적용 가능한 DTM)
    *   **인용문헌 분석:**
        *   **D1:** D1은 `DTM`을 사용하여 `contiguous tones`를 `non-contiguous tones`에 맵핑하여 `frequency spectrum`에 분산시키는 것을 개시합니다 (D1 [0108]-[0109], [0121]). 특히, "The DTM may be configured for mapping contiguous tones of each RU in the tone plan to a corresponding set of non-contiguous and non-punctured tones distributed across the frequency spectrum." (D1 [0123])라고 언급하여, `tone plan` 내의 `each RU`의 `contiguous tones`를 `frequency spectrum`에 걸쳐 분산된 `non-contiguous tones`에 맵핑하도록 `DTM`이 구성될 수 있음을 보여줍니다. 이는 `DTM`이 개별 `RU`의 톤 맵핑에 적용되면서도 그 결과가 `frequency spectrum` 전반에 걸쳐 분산됨을 시사합니다.
        *   **D2:** D2 역시 D1과 유사하게 `DTM`을 사용하여 톤을 분산 맵핑하는 것을 개시합니다 (D2 [0123]-[0124], [0126]). D2는 "The DTM may be configured for mapping contiguous tones of each RU in the tone plan to a corresponding set of non-contiguous and non-punctured tones distributed across the frequency spectrum." (D2 [0128])라고 언급합니다. 추가적으로, D2는 "The system may allocate pilot tones 935 such that pilot signals for each user (for example, each STA) are evenly spread over the channel bandwidth 905" (D2 [0142]) 및 "A minimum mapping distance (for example, to achieve the full power advantage) may depend on the logic RU size for the channel bandwidth 715" (D2 [0143])라고 개시합니다. 이러한 내용은 `DTM`이 `channel bandwidth` (즉, `frequency spectrum`) 전체에 걸쳐 톤을 균일하게 분산시키고 전력 이점을 얻기 위해 적용되는 개념을 더욱 명확히 제시합니다.
    *   **심사관 논거의 약점 및 진보성 주장:**
        *   심사관은 D1과 D2를 결합하여 "주파수 스펙트럼 전체에 적용 가능한 DTM"이 쉽게 도출될 수 있다고 주장합니다. 그러나 본원발명의 "DTM applicable to an entirety of the frequency spectrum"은 단순히 톤이 스펙트럼에 걸쳐 분산된다는 것을 넘어, `DTM` 자체가 *전체 주파수 스펙트럼을 대상으로 하는 단일의 또는 일관된 규칙*으로서 적용되어 맵핑을 수행한다는 의미를 내포합니다. D1과 D2는 `each RU`의 톤을 스펙트럼에 분산 맵핑하는 `DTM`에 대해 언급하지만, 이 `DTM`이 *전체 주파수 스펙트럼에 걸쳐 모든 `RU`에 대해 일관되게 적용되는 단일의 또는 글로벌한 파라미터*로서 기능한다는 점을 명시적으로 가르치거나 시사하지 않습니다.
        *   D1 [0123]과 D2 [0128]의 "contiguous tones of each RU... distributed across the frequency spectrum"은 개별 `RU`의 톤이 넓은 스펙트럼에 분산되는 결과를 설명하는 것이지, `DTM` 자체가 `entirety of the frequency spectrum`에 대한 *글로벌한 적용 가능성*을 가지는 파라미터임을 명확히 보여주지 않습니다. D2 [0142]의 "evenly spread over the channel bandwidth"는 파일럿 톤의 분산에 대한 것이며, D2 [0143]의 "minimum mapping distance... may depend on the logic RU size for the channel bandwidth"는 `DTM` 값이 `RU` 크기에 따라 달라질 수 있음을 시사하여, 오히려 `DTM`이 `entirety of the frequency spectrum`에 대해 *단일하게 적용되는 것이 아닐 수 있음*을 암시합니다.
        *   본원발명은 `DTM`을 `entirety of the frequency spectrum`에 적용함으로써, 여러 `RU`들이 동시에 맵핑될 때 전체 스펙트럼 관점에서 최적화된 톤 분산 및 `PSD` 제한 완화를 달성하는 데 목적이 있습니다 (본원발명 명세서 [0021], [0060]). 이는 단순히 개별 `RU`의 톤을 분산시키는 것을 넘어, 전체 시스템의 `PSD` 제한을 효율적으로 관리하고 총 송신 전력을 극대화하는 예측 불가한 현저한 효과를 제공할 수 있습니다. D1과 D2는 이러한 `DTM`의 `entirety of the frequency spectrum`에 대한 *글로벌한 적용* 및 그에 따른 시스템적 이점을 명시적으로 가르치거나 결합 동기를 제공하지 않습니다. 심사관의 결합 논리는 본원발명의 발명적 특징을 사후적으로 고찰(hindsight)한 것으로 보입니다.

### 대표 독립항: 청구항 21 (파싱(parsing)을 이용한 인접 톤의 비-인접 톤 변환 및 송신 스케줄링)

**1. 심사관 지적 요약:**
심사관은 청구항 21을 포함하는 "제2발명(청구항 21항 내지 30항 발명)"이 `PPDU`가 주파수 상에서 `non-contiguous tones`의 세트로 송수신되는 공통된 기술적 특징을 가지나, 이는 인용발명 1의 일반적인 `distributed RUs` 개념에 비해 개선된 것이 아니며, 그 외의 동일하거나 상응하는 기술적 특징을 포함하고 있지 않으므로 하나의 총괄적 발명의 개념을 형성하는 1군의 발명으로 볼 수 없다고 판단했습니다 (거절이유 1). 또한, 청구항 1에 대한 진보성 거절이유에서 D1, D2의 결합으로 쉽게 발명될 수 있다고 판단한 논리가 청구항 21에도 확장 적용될 수 있습니다.

**2. 심사관 지적 타당성 분석:**

*   **청구항 21의 핵심 구성:**
    *   `formatting a physical (PHY) layer convergence protocol (PLCP) protocol data unit (PPDU) for wireless transmission associated with a first frequency bandwidth that is wider than the bandwidth of the selected RU;` (선택된 `RU`의 대역폭보다 넓은 `first frequency bandwidth`와 연관된 `PPDU` 포맷팅)
    *   `parsing the plurality of contiguous tones of the selected RU to one or more sets of non-contiguous tones associated with a tone mapping number, wherein each set of non-contiguous tones spans a unique frequency segment of a second frequency bandwidth that is wider than the first frequency bandwidth;` (선택된 `RU`의 `contiguous tones`를 `parsing`하여, `first frequency bandwidth`보다 넓은 `second frequency bandwidth`의 `unique frequency segment`에 걸쳐 있는 `non-contiguous tones` 세트들로 변환)
    *   `scheduling a transmission of the PPDU over the one or more sets of non-contiguous tones.` (변환된 `non-contiguous tones` 세트를 통한 `PPDU` 송신 스케줄링)

*   **인용문헌 대비 및 진보성 주장:**
    *   **"parsing" 개념의 부재:** D1과 D2는 `contiguous tones`를 `non-contiguous tones`에 "mapping" (맵핑)하는 것을 개시하지만, 본원발명의 "parsing" (파싱) 개념을 명시적으로 가르치지 않습니다. "parsing"은 단순히 톤을 맵핑하여 분산시키는 것을 넘어, 특정 규칙에 따라 톤들을 분석하고 재구성하여 새로운 세트를 생성하는 보다 복잡한 처리 과정을 의미합니다. 본원발명 명세서 [0021], [0125]-[0126], [0219]-[0223]에 따르면, `parsing`은 `RU`의 `contiguous tones`를 `tone mapping number`와 연관된 `non-contiguous tones` 세트들로 변환하는 과정을 포함하며, 이는 `PSD` 제한 완화를 통한 송신 전력 증가를 목표로 합니다.
    *   **"unique frequency segment of a second frequency bandwidth that is wider than the first frequency bandwidth"의 특이성:** D1과 D2는 `non-contiguous tones`가 `frequency spectrum`에 걸쳐 "distributed" (분산)된다는 일반적인 개념을 개시합니다. 그러나 청구항 21은 `parsing` 결과로 생성된 `each set of non-contiguous tones`가 `first frequency bandwidth`보다 더 넓은 `second frequency bandwidth`의 "unique frequency segment" (고유 주파수 세그먼트)에 걸쳐 있다는 매우 구체적인 구조를 제시합니다. 이는 단순히 톤을 넓게 퍼뜨리는 것을 넘어, 특정 대역폭(`first frequency bandwidth`)으로 포맷된 `PPDU`를, 그보다 더 넓은 대역폭(`second frequency bandwidth`) 내의 *고유한 주파수 세그먼트*에 할당된 `non-contiguous tones`를 통해 송신하도록 스케줄링하는 다단계적이고 구조화된 톤 분산 및 할당 전략입니다.
    *   **결합 동기 부재 및 예측 불가한 현저한 효과:** D1과 D2는 `RU`의 대역폭보다 넓은 `first frequency bandwidth`에 맞춰 `PPDU`를 포맷하고, 이 `PPDU`를 `parsing`을 통해 `first frequency bandwidth`보다 더 넓은 `second frequency bandwidth` 내의 `unique frequency segment`에 걸쳐 있는 `non-contiguous tones`로 변환하여 송신 스케줄링하는 것에 대한 어떠한 가르침, 시사 또는 결합 동기를 제공하지 않습니다. 이러한 다단계적이고 계층적인 톤 분산 방식은 기존의 단순한 맵핑 방식으로는 달성하기 어려운, 특정 주파수 대역폭 내에서 `PSD` 제한을 더욱 효율적으로 완화하고, 다중 사용자 환경에서 간섭을 최소화하며, 유연한 자원 활용을 가능하게 하는 예측 불가한 현저한 효과를 제공할 수 있습니다. 심사관의 일반적인 `distributed RUs` 언급만으로는 청구항 21의 이러한 구체적이고 구조화된 `parsing` 및 `unique frequency segment` 할당 특징을 도출할 수 없습니다.

### 대표 독립항: 청구항 34 (트리거 프레임 기반 UL 송신을 위한 글로벌 DTM 맵핑)

**1. 심사관 지적 요약:**
심사관은 청구항 34를 포함하는 "제3발명(청구항 53항 내지 81항 발명)"이 `DTM` 기반으로 주파수 분산된 `non-contiguous tones`의 세트 및 더 넓은 주파수 스펙트럼을 통한 복제 `PPDU` 송수신에 대한 것이며, 이는 인용발명 1의 일반적인 `distributed RUs` 개념에 비해 개선된 것이 아니라고 판단했습니다 (거절이유 1). 또한, 청구항 1에 대한 진보성 거절이유에서 D1, D2의 결합으로 쉽게 발명될 수 있다고 판단한 논리가 청구항 34에도 확장 적용될 수 있다고 판단했습니다 (거절이유 2-7).

**2. 심사관 지적 타당성 분석:**

*   **청구항 34의 핵심 구성:**
    *   `receiving a trigger frame allocating a group of resource units (RUs) spanning a first frequency spectrum to one or more wireless communication devices for uplink (UL) transmissions, wherein a first RU of the group of RUs is allocated to the first wireless communication device, the first RU including a set of contiguous tones spanning a bandwidth of the first RU;` (`UL` 송신을 위해 `trigger frame`을 통해 `first frequency spectrum`에 걸쳐 있는 `RU` 그룹을 할당받음)
    *   `preparing a physical (PHY) layer convergence protocol (PLCP) protocol data unit (PPDU) for UL transmission based on the first frequency spectrum spanned by the group of RUs;` (`RU` 그룹에 의해 걸쳐 있는 `first frequency spectrum`에 기초하여 `UL` 송신용 `PPDU` 준비)
    *   `mapping the set of contiguous tones of the first RU to a first set of non-contiguous tones distributed across the first frequency spectrum based on a tone mapping distance (DTM) applicable to each RU of the group of RUs;` (`RU` 그룹의 `each RU`에 적용 가능한 `DTM`에 기초하여 `first RU`의 `contiguous tones`를 `first frequency spectrum`에 걸쳐 분산된 `non-contiguous tones`에 맵핑)
    *   `transmitting the PPDU over the first set of non-contiguous tones distributed across the first frequency spectrum.` (맵핑된 `non-contiguous tones`를 통해 `PPDU` 송신)

*   **인용문헌 대비 및 진보성 주장:**
    *   **"UL transmissions" 및 "trigger frame"의 특정 결합:** D1과 D2는 `UL` 송신 (D1 [0061], D2 [0086]) 및 `trigger frame` (D1 [0064]-[0065], D2 [0086])을 개시합니다. 그러나 청구항 34는 `UL` 송신을 위해 `trigger frame`을 통해 `RU` 그룹을 할당받는 특정 시나리오를 제시합니다. 이는 `UL` 다중 사용자 환경에서 `AP`가 `STA`들에게 자원을 할당하고 `UL` 송신을 조율하는 맥락을 명확히 합니다.
    *   **"DTM applicable to each RU of the group of RUs"의 글로벌 적용:** D1과 D2는 `DTM`이 `each RU`의 톤을 분산 맵핑하는 데 사용될 수 있음을 개시합니다 (D1 [0123], D2 [0128]). 그러나 청구항 34는 `DTM`이 `RU` 그룹의 `each RU`에 "applicable" (적용 가능)하다는 점을 명시합니다. 이는 `RU` 그룹 전체에 걸쳐 일관된 `DTM` 규칙이 적용되어, 그룹 내의 모든 `RU`들이 `first frequency spectrum`에 걸쳐 조화롭게 톤을 분산시킨다는 의미를 내포합니다. 즉, `DTM`이 개별 `RU`의 맵핑을 넘어서 `RU` 그룹 전체의 톤 분산 전략을 지배하는 *글로벌한 파라미터*로 기능한다는 점에서 차이가 있습니다.
    *   **"preparing a PPDU for UL transmission based on the first frequency spectrum spanned by the group of RUs"의 특이성:** `PPDU`를 `UL` 송신용으로 준비할 때, `first RU`의 대역폭이 아닌 `RU` 그룹에 의해 걸쳐 있는 `first frequency spectrum` 전체를 기반으로 한다는 점은, 개별 `RU` 단위의 송신이 아닌 `RU` 그룹 전체의 스펙트럼을 고려한 `UL` 송신 최적화를 목표로 함을 보여줍니다. 이는 `UL` 다중 사용자 환경에서 `PSD` 제한을 효율적으로 관리하고, `UL` 송신 전력을 증가시키며, `RU` 간 간섭을 줄이는 데 중요한 역할을 할 수 있습니다.
    *   **결합 동기 부재 및 예측 불가한 현저한 효과:** D1과 D2는 `UL` 송신, `trigger frame`, `DTM` 및 `distributed RUs`를 개시하지만, 이들을 결합하여 `UL` 송신을 위해 `trigger frame`을 통해 할당된 `RU` 그룹에 대해, `RU` 그룹 전체에 걸쳐 있는 `first frequency spectrum`을 기반으로 `PPDU`를 준비하고, `RU` 그룹의 `each RU`에 적용 가능한 `글로벌 DTM`을 사용하여 `first RU`의 톤을 `first frequency spectrum`에 걸쳐 분산 맵핑하는 구체적인 시스템적 접근 방식을 가르치거나 시사하지 않습니다. 본원발명 명세서 [0021], [0055], [0153]-[0155], [0242]-[0246]에 따르면, 이는 특히 `UL` 통신 환경에서 `trigger frame`을 통해 `RU`가 할당되고, 해당 `RU`의 `contiguous tones`를 `글로벌 DTM`을 사용하여 넓은 주파수 스펙트럼에 분산시켜 송신함으로써, `UL` 송신 전력을 효율적으로 증가시키는 것을 목적으로 합니다. 이러한 `UL` 다중 사용자 환경에서의 `글로벌 DTM` 적용은 `UL` 송신의 신뢰성, 효율성 및 시스템 용량을 향상시키는 예측 불가한 현저한 효과를 제공할 수 있습니다. 심사관의 "카테고리만 변경되었을 뿐... 쉽게 도출되는 수준"이라는 주장은 본원발명의 구체적인 `UL` 다중 사용자 시나리오에서의 `글로벌 DTM` 적용의 기술적 의의를 간과한 사후적 고찰로 보입니다.