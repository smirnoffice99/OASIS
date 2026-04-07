## 본원발명 분석

### 1. 거절 대상 독립항 식별

제시된 거절 대상 청구항(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52항) 중 다른 청구항을 인용하지 않는 독립항은 다음과 같습니다.

*   **청구항 1**
*   **청구항 13**
*   **청구항 21**
*   **청구항 34**

### 2. 유사한 독립항 그룹화 및 대표 독립항 식별

식별된 독립항들을 구성 및 기술적 특징에 따라 그룹화하고, 각 그룹의 대표 독립항을 선정합니다.

*   **그룹 1: 톤 맵핑 거리(DTM)를 이용한 인접 톤의 비-인접 톤 맵핑 및 송신**
    *   **대표 독립항: 청구항 1**
    *   유사 독립항: 청구항 13 (청구항 1의 장치(device) 발명)
        *   청구항 1은 무선 통신 방법을 청구하며, RU 선택, DTM을 이용한 인접 톤의 비-인접 톤 맵핑, 그리고 비-인접 톤을 통한 PPDU 송신을 포함합니다.
        *   청구항 13은 무선 통신 디바이스를 청구하며, 청구항 1과 동일한 기술적 특징을 프로세싱 시스템 및 인터페이스의 구성으로 표현합니다.

*   **그룹 2: 파싱(parsing)을 이용한 인접 톤의 비-인접 톤 변환 및 송신 스케줄링**
    *   **대표 독립항: 청구항 21**
        *   청구항 21은 무선 통신 방법을 청구하며, RU 선택, 선택된 RU의 대역폭보다 넓은 제1 주파수 대역폭에 대한 PPDU 포맷, 인접 톤의 비-인접 톤 파싱(parsing), 그리고 비-인접 톤을 통한 PPDU 송신 스케줄링을 포함합니다. 여기서 파싱된 비-인접 톤은 제1 주파수 대역폭보다 넓은 제2 주파수 대역폭의 고유 주파수 세그먼트에 걸쳐 있습니다.

*   **그룹 3: 트리거 프레임 기반 UL 송신을 위한 글로벌 DTM 맵핑**
    *   **대표 독립항: 청구항 34**
        *   청구항 34는 무선 통신 방법을 청구하며, UL 송신을 위한 RU 그룹 할당 트리거 프레임 수신, UL 송신을 위한 PPDU 준비, RU 그룹의 각 RU에 적용 가능한 글로벌 DTM에 기초한 인접 톤의 비-인접 톤 맵핑, 그리고 비-인접 톤을 통한 PPDU 송신을 포함합니다.

### 3. 식별된 대표 독립항들에 대한 본원발명 요약

#### **대표 독립항: 청구항 1**

*   **청구항 1 전문:**
    "A method for wireless communication by an apparatus of a wireless communication device, comprising:
    selecting a resource unit (RU) for transmitting a physical (PHY) layer convergence protocol (PLCP) protocol data unit (PPDU) over a wireless medium, wherein the selected RU comprises a portion of a tone plan for a frequency spectrum and includes a set of contiguous tones spanning a bandwidth of the selected RU;
    mapping the set of contiguous tones of the selected RU to a set of non-contiguous tones distributed across the frequency spectrum using a tone mapping distance (DTM) applicable to an entirety of the frequency spectrum; and
    transmitting the PPDU over the set of non-contiguous tones distributed across the frequency spectrum."

*   **본원발명 요약:**
    본원발명 청구항 1은 무선 통신 디바이스의 장치에 의한 무선 통신 방법을 청구합니다. 이 방법은 무선 매체를 통해 PPDU를 송신하기 위한 `resource unit (RU)`을 선택하는 단계를 포함하며, 선택된 `RU`는 주파수 스펙트럼에 대한 톤 계획의 일부분을 포함하고 해당 `RU`의 대역폭에 걸쳐 있는 `contiguous tones` 세트를 포함합니다. 핵심 기술적 특징은 선택된 `RU`의 `contiguous tones` 세트를 주파수 스펙트럼 전체에 적용 가능한 `tone mapping distance (DTM)`을 사용하여 주파수 스펙트럼에 걸쳐 분산된 `non-contiguous tones` 세트에 맵핑하는 단계, 그리고 이 `non-contiguous tones` 세트를 통해 `PPDU`를 송신하는 단계입니다. 이는 좁은 대역폭의 `RU`에 할당된 `contiguous tones`를 더 넓은 주파수 스펙트럼에 분산시켜 송신함으로써, `PSD (Power Spectral Density)` 제한을 완화하고 총 송신 전력을 증가시키는 것을 목적으로 합니다 (명세서 [0021], [0060], [0190]-[0193] 참조).

#### **대표 독립항: 청구항 21**

*   **청구항 21 전문:**
    "A method for wireless communication by an apparatus of a wireless communication device, comprising:
    selecting a resource unit (RU) of a group of RUs that collectively span a frequency spectrum, the selected RU including a plurality of contiguous tones spanning a bandwidth of the selected RU;
    formatting a physical (PHY) layer convergence protocol (PLCP) protocol data unit (PPDU) for wireless transmission associated with a first frequency bandwidth that is wider than the bandwidth of the selected RU;
    parsing the plurality of contiguous tones of the selected RU to one or more sets of non-contiguous tones associated with a tone mapping number, wherein each set of non-contiguous tones spans a unique frequency segment of a second frequency bandwidth that is wider than the first frequency bandwidth; and
    scheduling a transmission of the PPDU over the one or more sets of non-contiguous tones."

*   **본원발명 요약:**
    본원발명 청구항 21은 무선 통신 디바이스의 장치에 의한 무선 통신 방법을 청구합니다. 이 방법은 집합적으로 주파수 스펙트럼에 걸쳐 있는 `RU`들의 그룹 중 `RU`를 선택하는 단계를 포함하며, 선택된 `RU`는 해당 `RU`의 대역폭에 걸쳐 있는 복수의 `contiguous tones`를 포함합니다. 또한, 선택된 `RU`의 대역폭보다 더 넓은 `first frequency bandwidth`와 연관된 무선 송신을 위해 `PPDU`를 포맷하는 단계를 포함합니다. 핵심 기술적 특징은 선택된 `RU`의 복수의 `contiguous tones`를 `tone mapping number`와 연관된 하나 이상의 `non-contiguous tones` 세트들로 `parsing`하는 단계입니다. 이때, 각 `non-contiguous tones` 세트는 `first frequency bandwidth`보다 더 넓은 `second frequency bandwidth`의 고유 주파수 세그먼트에 걸쳐 있으며, 이 하나 이상의 `non-contiguous tones` 세트들을 통한 `PPDU`의 송신을 스케줄링합니다. 이는 `RU`의 `contiguous tones`를 `parsing`하여 더 넓은 대역폭의 고유 세그먼트에 분산된 `non-contiguous tones`로 변환함으로써, 역시 `PSD` 제한 완화를 통한 송신 전력 증가를 목표로 합니다 (명세서 [0021], [0125]-[0126], [0219]-[0223] 참조).

#### **대표 독립항: 청구항 34**

*   **청구항 34 전문:**
    "A method for wireless communication by an apparatus of a first wireless communication device, comprising:
    receiving a trigger frame allocating a group of resource units (RUs) spanning a first frequency spectrum to one or more wireless communication devices for uplink (UL) transmissions, wherein a first RU of the group of RUs is allocated to the first wireless communication device, the first RU including a set of contiguous tones spanning a bandwidth of the first RU;
    preparing a physical (PHY) layer convergence protocol (PLCP) protocol data unit (PPDU) for UL transmission based on the first frequency spectrum spanned by the group of RUs;
    mapping the set of contiguous tones of the first RU to a first set of non-contiguous tones distributed across the first frequency spectrum based on a tone mapping distance (DTM) applicable to each RU of the group of RUs; and
    transmitting the PPDU over the first set of non-contiguous tones distributed across the first frequency spectrum."

*   **본원발명 요약:**
    본원발명 청구항 34는 `first wireless communication device`의 장치에 의한 무선 통신 방법을 청구합니다. 이 방법은 `uplink (UL)` 송신들을 위해 `first frequency spectrum`에 걸쳐 있는 `RU`들의 그룹을 하나 이상의 무선 통신 디바이스들에 할당하는 `trigger frame`을 수신하는 단계를 포함하며, `RU`들의 그룹의 `first RU`는 `first wireless communication device`에 할당되고, `first RU`는 해당 `first RU`의 대역폭에 걸쳐 있는 `contiguous tones` 세트를 포함합니다. 또한, `RU`들의 그룹에 의해 걸쳐 있는 `first frequency spectrum`에 기초하여 `UL` 송신을 위한 `PPDU`를 준비하는 단계를 포함합니다. 핵심 기술적 특징은 `RU`들의 그룹의 각각의 `RU`에 적용 가능한 `tone mapping distance (DTM)`에 기초하여 `first RU`의 `contiguous tones` 세트를 `first frequency spectrum`에 걸쳐 분산된 `first set of non-contiguous tones`에 맵핑하는 단계, 그리고 이 `first set of non-contiguous tones`를 통해 `PPDU`를 송신하는 단계입니다. 이는 특히 `UL` 통신 환경에서 `trigger frame`을 통해 `RU`가 할당되고, 해당 `RU`의 `contiguous tones`를 글로벌 `DTM`을 사용하여 넓은 주파수 스펙트럼에 분산시켜 송신함으로써, `UL` 송신 전력을 효율적으로 증가시키는 것을 목적으로 합니다 (명세서 [0021], [0055], [0153]-[0155], [0242]-[0246] 참조).