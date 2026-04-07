# Office Action Response — Client Comment
**Case ID:** KR-TEST-001

---
## 1. Rejection Ground 1: Lack of Novelty and Inventive Step — Claims 1, 3, 5 / D1, D2

## II. Rejection reasons 1 and 2: lack of novelty or inventive step

D1: US10,123,456 (March 15, 2022)
D2: US9,876,543 (July 20, 2021)

1. Status of counterpart applications

We reviewed the prosecution of the US, EP, and JP counterpart applications to leverage similar claim amendments and arguments, where possible. A summary thereof is as follows:

We think that the features of the issued claims of counterpart US patent No. [patent number] are distinguishable from those disclosed in D1, D2. Thus, we will provide you with our comments below by making reference to the issued US claims.

(1) Since the same references were cited during the US prosecution, we will provide our comments below by making reference to the US response filed on (date).

(2) Although some of the references were cited during the US prosecution, since main reference D1 has been newly cited by the Korean examiner, we will provide our comments below based on our own analysis.

(3) Since none of the references were cited during the prosecution of the US, EP, or JP counterpart application, we will provide our comments below based on our own analysis.

(4) Please note that the US response filed on (date) in response to the OA with the same cited references as the subject Korean case was already leveraged on filing a response to the previous OA.

2. Our suggestion

The examiner alleged that claims 1, 3, 5 do not have novelty over D1. Furthermore, the examiner alleged that claims 1, 3, 5 do not have an inventive step over D1 and D2.

In order to overcome this rejection reason, we suggest amending claim 1 as follows:

A method for positioning a terminal device, the method comprising:
collecting a plurality of wireless signals;
calculating a first positioning reference value based on the collected wireless signals; and
determining a position by applying a Kalman filter or an extended Kalman filter to fuse the first positioning reference value with inertial sensor data.

This amendment is supported by paragraphs [0004], [0005] of the PCT application. A similar amendment can be made for the other independent claims. For more details, please refer to our Proposed Claims.

D1 relates to a Location Measurement System Using Wireless Signals. In this regard, D1 discloses a "location calculation means (positioning module)" (Column 3, Lines 15-40) that "processes the received signal data using a Kalman filter algorithm to produce a smoothed location estimate." However, D1 utilizes a Kalman filter for smoothing *wireless signal data itself*, not for *fusing a wireless signal-derived reference value with inertial sensor data*. D1 explicitly states that it "does NOT disclose: ... Fusion with inertial sensor (IMU) data." Thus, D1 fails to teach or suggest the feature of "applying a Kalman filter or an extended Kalman filter to fuse the first positioning reference value with inertial sensor data" as recited in proposed claim 1.

D2 relates to Wireless Signal Processing for Mobile Positioning. In this regard, D2 discloses combining "RSSI and RTT into a single composite reference value" (Paragraph [0045]-[0052]). However, D2 focuses on combining *different types of wireless signals* (metric fusion) to create a composite reference value. It does not involve inertial sensor data. D2 explicitly states that it "does NOT disclose: ... Integration with inertial sensor data." Thus, D2 fails to teach or suggest the feature of "applying a Kalman filter or an extended Kalman filter to fuse the first positioning reference value with inertial sensor data" as recited in proposed claim 1.

A similar argument can be made for the other independent claims. Therefore, if you approve of our suggestion, we will argue these points in an Argument, based on amended claims.

---
## 2. Rejection Ground 2: Lack of Clarity — Claim 7

## Rejection reason 2: unclear description of Claim 7

The examiner found that the meaning of "first positioning reference value" in claim 7 is unclear. The examiner further stated that multiple terms such as "측위 기준값" (positioning reference value), "위치 기준값" (position reference value), and "기준 측위값" (reference positioning value) are mixed throughout the specification, making it difficult to clearly understand the scope of the claim. This was cited as a violation of Article 42(4)2 of the Korean Patent Act, which requires claims to be clear and concise.

We acknowledge the examiner's concern regarding the clarity of claim 7 and propose an amendment to address this.

Under Korean patent law, claims must clearly and concisely define the invention, and the terms used therein must be clearly supported by the detailed description. While the examiner explicitly pointed to the clarity of "first positioning reference value" and term consistency, our review also identified that the phrase "dynamically adjusted according to a user movement pattern" in claim 7 lacks specific support in the detailed description. To fully comply with the requirements of Article 42(4) (including both clarity and support), we propose the following amendment.

In this regard, the present disclosure reads as follows.

*   "[0001] 본 발명의 위치 측정 방법은 단말기가 수집한 복수의 신호로부터 제1 측위 기준값을 산출하는 단계를 포함한다."
*   "[0002] 상기 제1 측위 기준값은 RSSI(수신신호강도), RTT(왕복 지연시간), AoA(도달각도) 중 적어도 하나를 포함하는 가중 평균값으로 정의된다."

Referring to the present disclosure, "first positioning reference value" is clearly defined in paragraph [0002] as "a weighted average value including at least one of RSSI (Received Signal Strength Indicator), RTT (Round Trip Time), and AoA (Angle of Arrival)". To enhance the clarity of this term within the claim itself and ensure its technical meaning is unambiguous, we propose to incorporate this definition directly into claim 7.

Regarding the examiner's comment on the mixing of terms, our review of the provided specification excerpt ([0001] to [0005]) and the claims did not identify the specific alternative terms mentioned ("위치 기준값", "기준 측위값"). However, we will ensure that "first positioning reference value" is consistently used throughout the entire specification to refer to the defined concept, thereby eliminating any potential ambiguity in the scope of protection.

Furthermore, claim 7, as originally filed, states that "the first positioning reference value is dynamically adjusted according to a user movement pattern." While this feature may represent an inventive concept, the current detailed description (paragraphs [0001] to [0005]) does not provide sufficient technical details or examples on *how* the "first positioning reference value" is "dynamically adjusted" based on "user movement patterns." This lack of specific disclosure renders this particular feature unsupported by the detailed description, which is a violation of Article 42(4)1. Therefore, to overcome this lack of support and ensure the claim is fully enabled, we propose to remove this unsupported phrase from claim 7.

Based on the above, we propose to amend claim 7 as follows:

**Original Claim 7:**
"7. The method of claim 1, wherein the first positioning reference value is dynamically adjusted according to a user movement pattern."

**Proposed Amended Claim 7:**
"7. The method of claim 1, wherein the first positioning reference value is **calculated as a weighted average value including at least one of RSSI (Received Signal Strength Indicator), RTT (Round Trip Time), and AoA (Angle of Arrival)**."

This amendment directly addresses the examiner's clarity concern by explicitly defining "first positioning reference value" within the claim, drawing from the clear definition provided in paragraph [0002] of the detailed description. Concurrently, by removing the unsupported phrase "dynamically adjusted according to a user movement pattern," we ensure that claim 7 fully complies with the support requirement of Article 42(4)1.

Therefore, we believe that the proposed amendment to claim 7 will effectively resolve the clarity issues raised by the examiner and overcome this rejection reason.

---
## 3. Rejection Ground 3: Lack of Unity of Invention — Claims 1, 2, 3, 4, 5, 6, 7, 8 / D1

## Rejection reason 3: lack of unity of invention

D1: US10,123,456 (Location Measurement System Using Wireless Signals)

The examiner alleged that claims 1-5 (hereinafter, method claims) and claims 6-8 (hereinafter, device claims) do not fall under a group of inventions so linked as to form a single general inventive concept. The examiner stated that the cited prior art D1 discloses both a location measurement method and a terminal device for implementing it, and thus, the method claims and device claims of the present application do not share a common special technical feature (STF) that is improved over D1.

Under Korean patent law, the requirement of unity of invention is fulfilled when there is a technical relationship among the inventions of the claims involving one or more of the same or corresponding special technical features. The expression, "special technical features," means improvements distinctive from the prior art, considered as a whole.

In this regard, we suggest amending independent claims 1 and 6 to incorporate the feature of "wherein the first positioning reference value is calculated as a weighted average combining RSSI, RTT, and AoA simultaneously."

D1 relates to a location measurement system using wireless signals, and discloses a reference value calculation method (Column 5, Lines 10-30) that computes a weighted average of distance estimates derived from RSSI values. However, D1 does not disclose any feature regarding calculating a positioning reference value as a weighted average combining multiple signal metrics such as RSSI, RTT, and AoA simultaneously. This specific combination of multiple signal metrics for calculating the first positioning reference value represents a significant improvement in positioning accuracy over the prior art, including D1, which relies primarily on RSSI-based distance estimates. Thus, we think that this feature, shared by proposed claims 1 and 6, is distinctive from the features disclosed in D1, and proposed claims 1 and 6 share the same special technical feature.

Therefore, if you approve of our suggestion, we will argue these points in an Argument, based on amended claims.

---
## Overall Strategy

**Overall Strategy**

The proposed response will involve both claim amendments and substantive arguments to address all rejection grounds. The application's strongest asset lies in the feature of "applying a Kalman filter or an extended Kalman filter to fuse the first positioning reference value with inertial sensor data." Consistency in defining and applying the "first positioning reference value" across all amended claims will be crucial for overcoming the clarity and unity rejections. We believe there is a good likelihood of overcoming these rejections with the proposed strategy.