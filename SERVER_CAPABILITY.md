# SERVER_CAPABILITY

## 文件資訊

- 盤點時間：2026-04-23 14:53:52 +08:00
- 盤點來源：`GET http://localhost:8091/fhir/metadata` + 專案設定檔（docker-compose / config）

## 1. FHIR version

- FHIR 版本：`4.0.1`
- HAPI 版本：`8.8.0`
- Implementation URL（metadata）：`http://localhost:8091/fhir`

## 2. 目前支援的 resource types

- 總數：`146`
- 清單：`Account`, `ActivityDefinition`, `AdverseEvent`, `AllergyIntolerance`, `Appointment`, `AppointmentResponse`, `AuditEvent`, `Basic`, `Binary`, `BiologicallyDerivedProduct`, `BodyStructure`, `Bundle`, `CapabilityStatement`, `CarePlan`, `CareTeam`, `CatalogEntry`, `ChargeItem`, `ChargeItemDefinition`, `Claim`, `ClaimResponse`, `ClinicalImpression`, `CodeSystem`, `Communication`, `CommunicationRequest`, `CompartmentDefinition`, `Composition`, `ConceptMap`, `Condition`, `Consent`, `Contract`, `Coverage`, `CoverageEligibilityRequest`, `CoverageEligibilityResponse`, `DetectedIssue`, `Device`, `DeviceDefinition`, `DeviceMetric`, `DeviceRequest`, `DeviceUseStatement`, `DiagnosticReport`, `DocumentManifest`, `DocumentReference`, `EffectEvidenceSynthesis`, `Encounter`, `Endpoint`, `EnrollmentRequest`, `EnrollmentResponse`, `EpisodeOfCare`, `EventDefinition`, `Evidence`, `EvidenceVariable`, `ExampleScenario`, `ExplanationOfBenefit`, `FamilyMemberHistory`, `Flag`, `Goal`, `GraphDefinition`, `Group`, `GuidanceResponse`, `HealthcareService`, `ImagingStudy`, `Immunization`, `ImmunizationEvaluation`, `ImmunizationRecommendation`, `ImplementationGuide`, `InsurancePlan`, `Invoice`, `Library`, `Linkage`, `List`, `Location`, `Measure`, `MeasureReport`, `Media`, `Medication`, `MedicationAdministration`, `MedicationDispense`, `MedicationKnowledge`, `MedicationRequest`, `MedicationStatement`, `MedicinalProduct`, `MedicinalProductAuthorization`, `MedicinalProductContraindication`, `MedicinalProductIndication`, `MedicinalProductIngredient`, `MedicinalProductInteraction`, `MedicinalProductManufactured`, `MedicinalProductPackaged`, `MedicinalProductPharmaceutical`, `MedicinalProductUndesirableEffect`, `MessageDefinition`, `MessageHeader`, `MolecularSequence`, `NamingSystem`, `NutritionOrder`, `Observation`, `ObservationDefinition`, `OperationDefinition`, `OperationOutcome`, `Organization`, `OrganizationAffiliation`, `Parameters`, `Patient`, `PaymentNotice`, `PaymentReconciliation`, `Person`, `PlanDefinition`, `Practitioner`, `PractitionerRole`, `Procedure`, `Provenance`, `Questionnaire`, `QuestionnaireResponse`, `RelatedPerson`, `RequestGroup`, `ResearchDefinition`, `ResearchElementDefinition`, `ResearchStudy`, `ResearchSubject`, `RiskAssessment`, `RiskEvidenceSynthesis`, `Schedule`, `SearchParameter`, `ServiceRequest`, `Slot`, `Specimen`, `SpecimenDefinition`, `StructureDefinition`, `StructureMap`, `Subscription`, `Substance`, `SubstanceNucleicAcid`, `SubstancePolymer`, `SubstanceProtein`, `SubstanceReferenceInformation`, `SubstanceSourceMaterial`, `SubstanceSpecification`, `SupplyDelivery`, `SupplyRequest`, `Task`, `TerminologyCapabilities`, `TestReport`, `TestScript`, `ValueSet`, `VerificationResult`, `VisionPrescription`

## 3. 每個 resource 支援的 REST interactions（read/search/create/update）

- 目前 146 種資源都具備下列互動（含更多）：
  - `read`
  - `search-type`
  - `create`
  - `update`
- 另外也支援：`vread`、`patch`、`delete`、`history-instance`、`history-type`

### Phase 1 建議正式支援（優先）

| Priority | Resource | 建議原因 |
|---|---|---|
| P0 | `Patient` | 病患主檔與身份識別核心（姓名、性別、生日、證號） |
| P0 | `Observation` | 問卷/行為/生物標記/收支等資料主載體 |
| P1 | `Practitioner` | 綁定治療醫師 |
| P1 | `CareTeam` | 醫病關係與團隊關聯 |
| P1 | `Questionnaire` / `QuestionnaireResponse` | 前端表單結構與答題回填 |
| P1 | `CodeSystem` / `ValueSet` / `StructureDefinition` | 驗證規則與術語控管 |

## 4. 每個 resource 支援的 search parameters

### 4.1 Phase 1 核心資源

- `Patient` search parameters：`birthdate`, `deceased`, `address-state`, `gender`, `_lastUpdated`, `link`, `language`, `address-country`, `_list`, `death-date`, `phonetic`, `telecom`, `address-city`, `email`, `given`, `identifier`, `address`, `general-practitioner`, `_security`, `active`, `address-postalcode`, `_filter`, `_profile`, `phone`, `_tag`, `organization`, `_has`, `address-use`, `name`, `_source`, `_id`, `family`
- `Observation` search parameters：`date`, `combo-data-absent-reason`, `code`, `component-data-absent-reason`, `subject`, `combo-code-value-quantity`, `_lastUpdated`, `value-concept`, `value-date`, `derived-from`, `focus`, `part-of`, `has-member`, `_list`, `code-value-string`, `component-code-value-quantity`, `based-on`, `code-value-date`, `patient`, `specimen`, `component-code`, `code-value-quantity`, `combo-code-value-concept`, `value-string`, `identifier`, `performer`, `combo-code`, `method`, `value-quantity`, `component-value-quantity`, `_security`, `data-absent-reason`, `combo-value-quantity`, `encounter`, `_filter`, `code-value-concept`, `_profile`, `_tag`, `_has`, `_source`, `component-code-value-concept`, `_id`, `component-value-concept`, `category`, `device`, `combo-value-concept`, `status`

### 4.2 全資源明細（逐 resource）

#### `Account`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`owner`, `identifier`, `period`, `subject`, `_lastUpdated`, `_security`, `type`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `name`, `_source`, `_id`, `status`

#### `ActivityDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `successor`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `derived-from`, `description`, `context-type`, `predecessor`, `composed-of`, `title`, `_list`, `context-quantity`, `depends-on`, `effective`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `topic`, `_source`, `_id`, `status`

#### `AdverseEvent`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `severity`, `recorder`, `study`, `actuality`, `subject`, `_lastUpdated`, `resultingcondition`, `substance`, `_security`, `_filter`, `_list`, `_profile`, `seriousness`, `_tag`, `_has`, `_source`, `location`, `_id`, `category`, `event`

#### `AllergyIntolerance`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `code`, `_lastUpdated`, `verification-status`, `criticality`, `clinical-status`, `type`, `_list`, `patient`, `severity`, `identifier`, `manifestation`, `recorder`, `_security`, `onset`, `_filter`, `asserter`, `route`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `category`, `last-date`

#### `Appointment`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `specialty`, `service-category`, `_lastUpdated`, `slot`, `reason-code`, `_list`, `based-on`, `patient`, `supporting-info`, `identifier`, `practitioner`, `appointment-type`, `part-status`, `service-type`, `_security`, `_filter`, `actor`, `_profile`, `_tag`, `_has`, `reason-reference`, `_source`, `location`, `_id`, `status`

#### `AppointmentResponse`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `practitioner`, `part-status`, `_lastUpdated`, `_security`, `appointment`, `_filter`, `actor`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `location`, `_id`

#### `AuditEvent`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `entity-type`, `agent`, `entity-role`, `_lastUpdated`, `source`, `type`, `altid`, `_list`, `agent-name`, `entity-name`, `subtype`, `patient`, `action`, `outcome`, `policy`, `address`, `_security`, `_filter`, `site`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `agent-role`, `entity`

#### `Basic`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `code`, `author`, `created`, `subject`, `_lastUpdated`, `_security`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`

#### `Binary`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `BiologicallyDerivedProduct`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `BodyStructure`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `morphology`, `_lastUpdated`, `_security`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `location`, `_id`

#### `Bundle`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `_lastUpdated`, `_security`, `message`, `type`, `_filter`, `_list`, `_profile`, `composition`, `_tag`, `_has`, `_source`, `_id`, `timestamp`

#### `CapabilityStatement`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `software`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `fhirversion`, `title`, `mode`, `_list`, `context-quantity`, `context`, `guide`, `context-type-quantity`, `resource-profile`, `resource`, `_security`, `format`, `version`, `supported-profile`, `url`, `_filter`, `_profile`, `_tag`, `security-service`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`

#### `CarePlan`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `care-team`, `subject`, `_lastUpdated`, `part-of`, `_list`, `based-on`, `patient`, `activity-date`, `instantiates-uri`, `activity-code`, `identifier`, `goal`, `performer`, `replaces`, `_security`, `instantiates-canonical`, `encounter`, `intent`, `activity-reference`, `_filter`, `condition`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `category`, `status`

#### `CareTeam`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `subject`, `_lastUpdated`, `_security`, `encounter`, `participant`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`, `category`, `status`

#### `CatalogEntry`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `ChargeItem`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`performing-organization`, `code`, `subject`, `_lastUpdated`, `occurrence`, `entered-date`, `_list`, `performer-function`, `factor-override`, `patient`, `price-override`, `context`, `enterer`, `identifier`, `quantity`, `_security`, `_filter`, `_profile`, `service`, `_tag`, `_has`, `_source`, `_id`, `performer-actor`, `account`, `requesting-organization`

#### `ChargeItemDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `_security`, `description`, `context-type`, `title`, `version`, `url`, `_filter`, `_list`, `context-quantity`, `effective`, `_profile`, `_tag`, `_has`, `context`, `publisher`, `_source`, `_id`, `context-type-quantity`, `status`

#### `Claim`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`care-team`, `use`, `_lastUpdated`, `payee`, `_list`, `provider`, `insurer`, `patient`, `detail-udi`, `enterer`, `procedure-udi`, `item-udi`, `identifier`, `created`, `_security`, `encounter`, `priority`, `_filter`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `subdetail-udi`, `facility`, `status`

#### `ClaimResponse`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `request`, `created`, `use`, `_lastUpdated`, `_security`, `payment-date`, `requestor`, `_filter`, `_list`, `disposition`, `_profile`, `insurer`, `patient`, `_tag`, `_has`, `_source`, `_id`, `outcome`, `status`

#### `ClinicalImpression`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `previous`, `finding-code`, `assessor`, `subject`, `_lastUpdated`, `_security`, `encounter`, `finding-ref`, `_filter`, `_list`, `problem`, `_profile`, `patient`, `_tag`, `_has`, `supporting-info`, `investigation`, `_source`, `_id`, `status`

#### `CodeSystem`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `code`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `language`, `title`, `_list`, `context-quantity`, `context`, `context-type-quantity`, `identifier`, `content-mode`, `_security`, `version`, `url`, `_filter`, `supplements`, `system`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`

#### `Communication`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `subject`, `_lastUpdated`, `_security`, `instantiates-canonical`, `part-of`, `received`, `encounter`, `medium`, `sent`, `_filter`, `_list`, `based-on`, `_profile`, `sender`, `patient`, `_tag`, `_has`, `recipient`, `_source`, `instantiates-uri`, `_id`, `category`, `status`

#### `CommunicationRequest`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`authored`, `subject`, `_lastUpdated`, `medium`, `occurrence`, `_list`, `group-identifier`, `based-on`, `patient`, `requester`, `identifier`, `replaces`, `_security`, `encounter`, `priority`, `_filter`, `_profile`, `sender`, `_tag`, `_has`, `recipient`, `_source`, `_id`, `category`, `status`

#### `CompartmentDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `code`, `context-type-value`, `resource`, `_lastUpdated`, `_security`, `description`, `context-type`, `version`, `url`, `_filter`, `_list`, `context-quantity`, `_profile`, `_tag`, `_has`, `context`, `name`, `publisher`, `_source`, `_id`, `context-type-quantity`, `status`

#### `Composition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `subject`, `_lastUpdated`, `confidentiality`, `section`, `type`, `title`, `_list`, `patient`, `context`, `identifier`, `period`, `related-id`, `author`, `_security`, `encounter`, `attester`, `_filter`, `entry`, `_profile`, `related-ref`, `_tag`, `_has`, `_source`, `_id`, `category`, `status`

#### `ConceptMap`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `other`, `context-type-value`, `dependson`, `target-system`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `source`, `title`, `_list`, `context-quantity`, `source-uri`, `context`, `context-type-quantity`, `source-system`, `target-code`, `target-uri`, `identifier`, `product`, `_security`, `version`, `url`, `target`, `_filter`, `source-code`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`

#### `Condition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`onset-info`, `code`, `evidence`, `subject`, `_lastUpdated`, `verification-status`, `clinical-status`, `onset-date`, `_list`, `abatement-date`, `patient`, `abatement-age`, `evidence-detail`, `severity`, `identifier`, `recorded-date`, `_security`, `encounter`, `_filter`, `asserter`, `_profile`, `stage`, `abatement-string`, `_tag`, `_has`, `onset-age`, `_source`, `_id`, `body-site`, `category`

#### `Consent`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `period`, `data`, `purpose`, `_lastUpdated`, `_security`, `source-reference`, `_filter`, `actor`, `_list`, `security-label`, `_profile`, `patient`, `_tag`, `organization`, `scope`, `_has`, `action`, `_source`, `consentor`, `_id`, `category`, `status`

#### `Contract`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `instantiates`, `subject`, `_lastUpdated`, `_security`, `url`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `authority`, `domain`, `_has`, `_source`, `_id`, `issued`, `signer`, `status`

#### `Coverage`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `subscriber`, `_lastUpdated`, `_security`, `type`, `_filter`, `_list`, `payor`, `_profile`, `beneficiary`, `patient`, `_tag`, `_has`, `class-value`, `_source`, `_id`, `class-type`, `dependent`, `policy-holder`, `status`

#### `CoverageEligibilityRequest`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `created`, `_lastUpdated`, `_security`, `_filter`, `_list`, `_profile`, `provider`, `patient`, `_tag`, `_has`, `enterer`, `_source`, `_id`, `facility`, `status`

#### `CoverageEligibilityResponse`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `request`, `created`, `_lastUpdated`, `_security`, `requestor`, `_filter`, `_list`, `disposition`, `_profile`, `insurer`, `patient`, `_tag`, `_has`, `_source`, `_id`, `outcome`, `status`

#### `DetectedIssue`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `code`, `author`, `_lastUpdated`, `_security`, `_filter`, `_list`, `identified`, `_profile`, `patient`, `_tag`, `_has`, `implicated`, `_source`, `_id`

#### `Device`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`udi-di`, `identifier`, `udi-carrier`, `device-name`, `_lastUpdated`, `_security`, `type`, `url`, `manufacturer`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `organization`, `_has`, `_source`, `location`, `model`, `_id`, `status`

#### `DeviceDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `identifier`, `parent`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `type`, `_filter`

#### `DeviceMetric`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `parent`, `_lastUpdated`, `_security`, `source`, `type`, `_filter`, `_list`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `category`

#### `DeviceRequest`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`insurance`, `code`, `subject`, `_lastUpdated`, `_list`, `group-identifier`, `based-on`, `patient`, `instantiates-uri`, `requester`, `identifier`, `performer`, `event-date`, `_security`, `instantiates-canonical`, `encounter`, `authored-on`, `intent`, `_filter`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `device`, `prior-request`, `status`

#### `DeviceUseStatement`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `subject`, `_lastUpdated`, `_security`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`, `device`

#### `DiagnosticReport`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `code`, `subject`, `_lastUpdated`, `media`, `conclusion`, `result`, `_list`, `based-on`, `patient`, `specimen`, `issued`, `identifier`, `performer`, `_security`, `encounter`, `_filter`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `category`, `results-interpreter`, `status`

#### `DocumentManifest`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `item`, `related-id`, `author`, `created`, `subject`, `_lastUpdated`, `_security`, `description`, `source`, `type`, `_filter`, `_list`, `_profile`, `related-ref`, `patient`, `_tag`, `_has`, `recipient`, `_source`, `_id`, `status`

#### `DocumentReference`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `subject`, `_lastUpdated`, `description`, `language`, `type`, `relation`, `setting`, `_list`, `related`, `patient`, `event`, `relationship`, `authenticator`, `identifier`, `period`, `custodian`, `author`, `_security`, `format`, `encounter`, `contenttype`, `_filter`, `security-label`, `_profile`, `_tag`, `_has`, `_source`, `location`, `_id`, `category`, `relatesto`, `facility`, `status`

#### `EffectEvidenceSynthesis`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `title`, `_list`, `context-quantity`, `effective`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`

#### `Encounter`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `participant-type`, `subject`, `_lastUpdated`, `appointment`, `part-of`, `type`, `participant`, `reason-code`, `_list`, `based-on`, `patient`, `location-period`, `special-arrangement`, `class`, `identifier`, `practitioner`, `_security`, `episode-of-care`, `length`, `diagnosis`, `_filter`, `_profile`, `_tag`, `_has`, `reason-reference`, `_source`, `location`, `service-provider`, `_id`, `account`, `status`

#### `Endpoint`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `_lastUpdated`, `_security`, `_filter`, `payload-type`, `_list`, `_profile`, `_tag`, `connection-type`, `organization`, `_has`, `name`, `_source`, `_id`, `status`

#### `EnrollmentRequest`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `subject`, `_lastUpdated`, `_security`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`, `status`

#### `EnrollmentResponse`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `identifier`, `request`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `status`, `_filter`

#### `EpisodeOfCare`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `_lastUpdated`, `_security`, `type`, `incoming-referral`, `_filter`, `_list`, `condition`, `_profile`, `patient`, `_tag`, `organization`, `_has`, `_source`, `_id`, `care-manager`, `status`

#### `EventDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `successor`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `derived-from`, `description`, `context-type`, `predecessor`, `composed-of`, `title`, `_list`, `context-quantity`, `depends-on`, `effective`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `topic`, `_source`, `_id`, `status`

#### `Evidence`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `successor`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `derived-from`, `description`, `context-type`, `predecessor`, `composed-of`, `title`, `_list`, `context-quantity`, `depends-on`, `effective`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `topic`, `_source`, `_id`, `status`

#### `EvidenceVariable`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `successor`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `derived-from`, `description`, `context-type`, `predecessor`, `composed-of`, `title`, `_list`, `context-quantity`, `depends-on`, `effective`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `topic`, `_source`, `_id`, `status`

#### `ExampleScenario`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `_security`, `context-type`, `version`, `url`, `_filter`, `_list`, `context-quantity`, `_profile`, `_tag`, `_has`, `context`, `name`, `publisher`, `_source`, `_id`, `context-type-quantity`, `status`

#### `ExplanationOfBenefit`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`care-team`, `_lastUpdated`, `payee`, `_list`, `provider`, `patient`, `detail-udi`, `claim`, `enterer`, `procedure-udi`, `item-udi`, `coverage`, `identifier`, `created`, `_security`, `encounter`, `_filter`, `disposition`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `subdetail-udi`, `facility`, `status`

#### `FamilyMemberHistory`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `code`, `_lastUpdated`, `sex`, `_security`, `instantiates-canonical`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `instantiates-uri`, `_id`, `relationship`, `status`

#### `Flag`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `author`, `subject`, `_lastUpdated`, `_security`, `encounter`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`

#### `Goal`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `subject`, `_lastUpdated`, `_security`, `start-date`, `_filter`, `_list`, `lifecycle-status`, `_profile`, `achievement-status`, `patient`, `_tag`, `_has`, `_source`, `_id`, `category`, `target-date`

#### `GraphDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `_security`, `start`, `description`, `context-type`, `version`, `url`, `_filter`, `_list`, `context-quantity`, `_profile`, `_tag`, `_has`, `context`, `name`, `publisher`, `_source`, `_id`, `context-type-quantity`, `status`

#### `Group`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`actual`, `identifier`, `managing-entity`, `code`, `_lastUpdated`, `_security`, `type`, `characteristic`, `_filter`, `_list`, `characteristic-value`, `_profile`, `_tag`, `_has`, `member`, `_source`, `exclude`, `_id`, `value`

#### `GuidanceResponse`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `request`, `subject`, `_lastUpdated`, `_security`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`

#### `HealthcareService`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `specialty`, `service-category`, `_lastUpdated`, `service-type`, `_security`, `active`, `program`, `characteristic`, `_filter`, `_list`, `endpoint`, `_profile`, `coverage-area`, `_tag`, `organization`, `_has`, `name`, `_source`, `location`, `_id`

#### `ImagingStudy`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`reason`, `dicom-class`, `instance`, `modality`, `subject`, `_lastUpdated`, `_list`, `endpoint`, `patient`, `identifier`, `bodysite`, `performer`, `_security`, `interpreter`, `started`, `encounter`, `_filter`, `referrer`, `_profile`, `series`, `_tag`, `_has`, `_source`, `_id`, `basedon`, `status`

#### `Immunization`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `lot-number`, `_lastUpdated`, `status-reason`, `reason-code`, `manufacturer`, `_list`, `patient`, `reaction-date`, `identifier`, `performer`, `reaction`, `_security`, `_filter`, `_profile`, `target-disease`, `series`, `_tag`, `vaccine-code`, `_has`, `reason-reference`, `_source`, `location`, `_id`, `status`

#### `ImmunizationEvaluation`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `_lastUpdated`, `_security`, `dose-status`, `immunization-event`, `_filter`, `_list`, `_profile`, `target-disease`, `patient`, `_tag`, `_has`, `_source`, `_id`, `status`

#### `ImmunizationRecommendation`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `_lastUpdated`, `_security`, `vaccine-type`, `_filter`, `_list`, `_profile`, `target-disease`, `patient`, `_tag`, `_has`, `_source`, `information`, `_id`, `support`, `status`

#### `ImplementationGuide`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `experimental`, `global`, `title`, `_list`, `context-quantity`, `depends-on`, `context`, `context-type-quantity`, `resource`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`

#### `InsurancePlan`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `address`, `address-state`, `owned-by`, `_lastUpdated`, `_security`, `type`, `address-postalcode`, `address-country`, `administered-by`, `_filter`, `_list`, `endpoint`, `phonetic`, `_profile`, `_tag`, `_has`, `address-use`, `name`, `_source`, `_id`, `address-city`, `status`

#### `Invoice`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `totalgross`, `participant-role`, `subject`, `_lastUpdated`, `_security`, `type`, `issuer`, `participant`, `totalnet`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `recipient`, `_source`, `_id`, `account`, `status`

#### `Library`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `successor`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `derived-from`, `description`, `context-type`, `predecessor`, `composed-of`, `title`, `type`, `_list`, `context-quantity`, `depends-on`, `effective`, `context`, `content-type`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `topic`, `_source`, `_id`, `status`

#### `Linkage`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `item`, `_profile`, `author`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `source`, `_filter`

#### `List`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `empty-reason`, `item`, `code`, `notes`, `subject`, `_lastUpdated`, `_security`, `encounter`, `source`, `title`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`, `status`

#### `Location`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `partof`, `address`, `address-state`, `_lastUpdated`, `_security`, `operational-status`, `type`, `address-postalcode`, `address-country`, `_filter`, `_list`, `endpoint`, `_profile`, `_tag`, `organization`, `_has`, `address-use`, `name`, `_source`, `_id`, `near`, `address-city`, `status`

#### `Measure`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `successor`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `derived-from`, `description`, `context-type`, `predecessor`, `composed-of`, `title`, `_list`, `context-quantity`, `depends-on`, `effective`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `topic`, `_source`, `_id`, `status`

#### `MeasureReport`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `period`, `subject`, `_lastUpdated`, `_security`, `reporter`, `_filter`, `_list`, `measure`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`, `evaluated-resource`, `status`

#### `Media`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `modality`, `created`, `subject`, `_lastUpdated`, `_security`, `encounter`, `type`, `operator`, `_filter`, `_list`, `site`, `view`, `based-on`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`, `device`, `status`

#### `Medication`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `code`, `ingredient`, `lot-number`, `_lastUpdated`, `_security`, `manufacturer`, `_filter`, `ingredient-code`, `_list`, `_profile`, `form`, `_tag`, `_has`, `_source`, `_id`, `expiration-date`, `status`

#### `MedicationAdministration`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `request`, `code`, `performer`, `subject`, `_lastUpdated`, `_security`, `medication`, `reason-given`, `_filter`, `_list`, `_profile`, `patient`, `effective-time`, `_tag`, `_has`, `context`, `reason-not-given`, `_source`, `_id`, `device`, `status`

#### `MedicationDispense`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `code`, `performer`, `receiver`, `subject`, `_lastUpdated`, `_security`, `destination`, `medication`, `responsibleparty`, `type`, `whenhandedover`, `whenprepared`, `_filter`, `_list`, `_profile`, `prescription`, `patient`, `_tag`, `_has`, `context`, `_source`, `_id`, `status`

#### `MedicationKnowledge`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`code`, `ingredient`, `doseform`, `_lastUpdated`, `_security`, `classification-type`, `monograph-type`, `classification`, `manufacturer`, `_filter`, `ingredient-code`, `_list`, `source-cost`, `_profile`, `monitoring-program-name`, `monograph`, `_tag`, `_has`, `_source`, `monitoring-program-type`, `_id`, `status`

#### `MedicationRequest`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `code`, `authoredon`, `subject`, `_lastUpdated`, `_list`, `patient`, `intended-performer`, `intended-performertype`, `requester`, `identifier`, `intended-dispenser`, `_security`, `medication`, `encounter`, `priority`, `intent`, `_filter`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `category`, `status`

#### `MedicationStatement`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `code`, `subject`, `_lastUpdated`, `_security`, `medication`, `part-of`, `source`, `_filter`, `_list`, `effective`, `_profile`, `patient`, `_tag`, `_has`, `context`, `_source`, `_id`, `category`, `status`

#### `MedicinalProduct`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `identifier`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `name`, `_source`, `name-language`, `_id`, `_filter`

#### `MedicinalProductAuthorization`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`country`, `identifier`, `subject`, `_lastUpdated`, `_security`, `holder`, `_filter`, `_list`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `status`

#### `MedicinalProductContraindication`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `subject`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `MedicinalProductIndication`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `subject`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `MedicinalProductIngredient`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `MedicinalProductInteraction`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `subject`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `MedicinalProductManufactured`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `MedicinalProductPackaged`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `identifier`, `_profile`, `subject`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `MedicinalProductPharmaceutical`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `identifier`, `route`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `target-species`, `_filter`

#### `MedicinalProductUndesirableEffect`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `subject`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `MessageDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `parent`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `focus`, `context-type`, `title`, `_list`, `context-quantity`, `context`, `event`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `category`, `status`

#### `MessageHeader`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`code`, `receiver`, `author`, `_lastUpdated`, `_security`, `destination`, `focus`, `source`, `target`, `_filter`, `_list`, `destination-uri`, `_profile`, `sender`, `source-uri`, `_tag`, `responsible`, `_has`, `enterer`, `response-id`, `_source`, `_id`, `event`

#### `MolecularSequence`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `referenceseqid-variant-coordinate`, `_lastUpdated`, `chromosome`, `_security`, `type`, `window-end`, `window-start`, `variant-end`, `_filter`, `_list`, `chromosome-variant-coordinate`, `_profile`, `patient`, `_tag`, `_has`, `variant-start`, `_source`, `chromosome-window-coordinate`, `_id`, `referenceseqid-window-coordinate`, `referenceseqid`

#### `NamingSystem`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `type`, `_list`, `context-quantity`, `contact`, `responsible`, `context`, `telecom`, `value`, `context-type-quantity`, `period`, `kind`, `_security`, `id-type`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`

#### `NutritionOrder`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `_lastUpdated`, `_security`, `instantiates-canonical`, `encounter`, `oraldiet`, `additive`, `_filter`, `_list`, `datetime`, `_profile`, `provider`, `patient`, `supplement`, `_tag`, `_has`, `formula`, `_source`, `instantiates-uri`, `_id`, `status`

#### `Observation`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `combo-data-absent-reason`, `code`, `component-data-absent-reason`, `subject`, `combo-code-value-quantity`, `_lastUpdated`, `value-concept`, `value-date`, `derived-from`, `focus`, `part-of`, `has-member`, `_list`, `code-value-string`, `component-code-value-quantity`, `based-on`, `code-value-date`, `patient`, `specimen`, `component-code`, `code-value-quantity`, `combo-code-value-concept`, `value-string`, `identifier`, `performer`, `combo-code`, `method`, `value-quantity`, `component-value-quantity`, `_security`, `data-absent-reason`, `combo-value-quantity`, `encounter`, `_filter`, `code-value-concept`, `_profile`, `_tag`, `_has`, `_source`, `component-code-value-concept`, `_id`, `component-value-concept`, `category`, `device`, `combo-value-concept`, `status`

#### `ObservationDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `OperationDefinition`
- REST interactions：`read`, `search-type`, `update`, `vread`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `code`, `instance`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `title`, `type`, `_list`, `context-quantity`, `output-profile`, `context`, `context-type-quantity`, `kind`, `_security`, `version`, `url`, `_filter`, `input-profile`, `system`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`, `base`

#### `OperationOutcome`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `Organization`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `partof`, `address`, `address-state`, `_lastUpdated`, `_security`, `active`, `type`, `address-postalcode`, `address-country`, `_filter`, `_list`, `endpoint`, `phonetic`, `_profile`, `_tag`, `_has`, `address-use`, `name`, `_source`, `_id`, `address-city`

#### `OrganizationAffiliation`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `specialty`, `role`, `_lastUpdated`, `_security`, `active`, `primary-organization`, `network`, `_filter`, `_list`, `endpoint`, `_profile`, `phone`, `service`, `_tag`, `_has`, `participating-organization`, `_source`, `location`, `telecom`, `_id`, `email`

#### `Parameters`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `Patient`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`birthdate`, `deceased`, `address-state`, `gender`, `_lastUpdated`, `link`, `language`, `address-country`, `_list`, `death-date`, `phonetic`, `telecom`, `address-city`, `email`, `given`, `identifier`, `address`, `general-practitioner`, `_security`, `active`, `address-postalcode`, `_filter`, `_profile`, `phone`, `_tag`, `organization`, `_has`, `address-use`, `name`, `_source`, `_id`, `family`

#### `PaymentNotice`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `request`, `created`, `_lastUpdated`, `_security`, `payment-status`, `_filter`, `_list`, `_profile`, `provider`, `response`, `_tag`, `_has`, `_source`, `_id`, `status`

#### `PaymentReconciliation`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `request`, `created`, `_lastUpdated`, `_security`, `requestor`, `_filter`, `_list`, `disposition`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `outcome`, `payment-issuer`, `status`

#### `Person`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`birthdate`, `address-state`, `gender`, `_lastUpdated`, `link`, `address-country`, `_list`, `phonetic`, `patient`, `telecom`, `address-city`, `email`, `identifier`, `address`, `practitioner`, `_security`, `relatedperson`, `address-postalcode`, `_filter`, `_profile`, `phone`, `_tag`, `organization`, `_has`, `address-use`, `name`, `_source`, `_id`

#### `PlanDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `successor`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `derived-from`, `description`, `context-type`, `predecessor`, `composed-of`, `title`, `type`, `_list`, `context-quantity`, `depends-on`, `effective`, `context`, `definition`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `topic`, `_source`, `_id`, `status`

#### `Practitioner`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`address-state`, `gender`, `_lastUpdated`, `address-country`, `_list`, `phonetic`, `telecom`, `address-city`, `communication`, `email`, `given`, `identifier`, `address`, `_security`, `active`, `address-postalcode`, `_filter`, `_profile`, `phone`, `_tag`, `_has`, `address-use`, `name`, `_source`, `_id`, `family`

#### `PractitionerRole`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `specialty`, `role`, `practitioner`, `_lastUpdated`, `_security`, `active`, `_filter`, `_list`, `endpoint`, `_profile`, `phone`, `service`, `_tag`, `organization`, `_has`, `_source`, `telecom`, `location`, `_id`, `email`

#### `Procedure`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `code`, `subject`, `_lastUpdated`, `part-of`, `reason-code`, `_list`, `based-on`, `patient`, `instantiates-uri`, `identifier`, `performer`, `_security`, `instantiates-canonical`, `encounter`, `_filter`, `_profile`, `_tag`, `_has`, `reason-reference`, `_source`, `location`, `_id`, `category`, `status`

#### `Provenance`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`agent-type`, `agent`, `signature-type`, `_lastUpdated`, `_security`, `recorded`, `when`, `target`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `location`, `_id`, `agent-role`, `entity`

#### `Questionnaire`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `code`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `title`, `_list`, `context-quantity`, `effective`, `context`, `definition`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `subject-type`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`

#### `QuestionnaireResponse`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`authored`, `identifier`, `questionnaire`, `author`, `subject`, `_lastUpdated`, `_security`, `part-of`, `encounter`, `source`, `_filter`, `_list`, `based-on`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`, `status`

#### `RelatedPerson`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`birthdate`, `address-state`, `gender`, `_lastUpdated`, `address-country`, `_list`, `phonetic`, `patient`, `telecom`, `address-city`, `relationship`, `email`, `identifier`, `address`, `_security`, `active`, `address-postalcode`, `_filter`, `_profile`, `phone`, `_tag`, `_has`, `address-use`, `name`, `_source`, `_id`

#### `RequestGroup`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`authored`, `identifier`, `code`, `author`, `subject`, `_lastUpdated`, `_security`, `instantiates-canonical`, `encounter`, `priority`, `intent`, `participant`, `_filter`, `_list`, `group-identifier`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `instantiates-uri`, `_id`, `status`

#### `ResearchDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `successor`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `derived-from`, `description`, `context-type`, `predecessor`, `composed-of`, `title`, `_list`, `context-quantity`, `depends-on`, `effective`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `topic`, `_source`, `_id`, `status`

#### `ResearchElementDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `successor`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `derived-from`, `description`, `context-type`, `predecessor`, `composed-of`, `title`, `_list`, `context-quantity`, `depends-on`, `effective`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `topic`, `_source`, `_id`, `status`

#### `ResearchStudy`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `partof`, `sponsor`, `_lastUpdated`, `_security`, `focus`, `principalinvestigator`, `title`, `_filter`, `_list`, `protocol`, `site`, `_profile`, `_tag`, `_has`, `_source`, `location`, `_id`, `category`, `keyword`, `status`

#### `ResearchSubject`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `study`, `individual`, `_lastUpdated`, `_security`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`, `status`

#### `RiskAssessment`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `performer`, `method`, `probability`, `subject`, `_lastUpdated`, `_security`, `encounter`, `_filter`, `_list`, `condition`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `risk`, `_id`

#### `RiskEvidenceSynthesis`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `title`, `_list`, `context-quantity`, `effective`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`

#### `Schedule`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `specialty`, `service-category`, `_lastUpdated`, `service-type`, `_security`, `active`, `_filter`, `actor`, `_list`, `_profile`, `_tag`, `_has`, `_source`, `_id`

#### `SearchParameter`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `code`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `derived-from`, `context-type`, `type`, `_list`, `context-quantity`, `context`, `context-type-quantity`, `_security`, `version`, `url`, `target`, `_filter`, `component`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`, `base`

#### `ServiceRequest`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`authored`, `code`, `requisition`, `subject`, `_lastUpdated`, `occurrence`, `_list`, `based-on`, `patient`, `specimen`, `instantiates-uri`, `requester`, `identifier`, `performer`, `replaces`, `_security`, `instantiates-canonical`, `encounter`, `priority`, `intent`, `performer-type`, `_filter`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `body-site`, `category`, `status`

#### `Slot`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `specialty`, `service-category`, `appointment-type`, `_lastUpdated`, `service-type`, `_security`, `start`, `_filter`, `_list`, `schedule`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `status`

#### `Specimen`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`container`, `container-id`, `identifier`, `parent`, `bodysite`, `subject`, `_lastUpdated`, `_security`, `collected`, `accession`, `type`, `collector`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`, `status`

#### `SpecimenDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`container`, `_list`, `identifier`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `type`, `_filter`

#### `StructureDefinition`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `experimental`, `title`, `type`, `_list`, `context-quantity`, `path`, `context`, `base-path`, `keyword`, `context-type-quantity`, `identifier`, `valueset`, `kind`, `_security`, `abstract`, `version`, `url`, `_filter`, `_profile`, `ext-context`, `_tag`, `_has`, `name`, `publisher`, `_source`, `derivation`, `_id`, `status`, `base`

#### `StructureMap`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `identifier`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `_security`, `description`, `context-type`, `title`, `version`, `url`, `_filter`, `_list`, `context-quantity`, `_profile`, `_tag`, `_has`, `context`, `name`, `publisher`, `_source`, `_id`, `context-type-quantity`, `status`

#### `Subscription`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`criteria`, `_lastUpdated`, `_security`, `type`, `url`, `_filter`, `_list`, `_profile`, `payload`, `_tag`, `contact`, `_has`, `_source`, `_id`, `status`

#### `Substance`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `container-identifier`, `code`, `quantity`, `_lastUpdated`, `_security`, `_filter`, `_list`, `_profile`, `_tag`, `_has`, `substance-reference`, `_source`, `_id`, `expiry`, `category`, `status`

#### `SubstanceNucleicAcid`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `SubstancePolymer`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `SubstanceProtein`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `SubstanceReferenceInformation`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `SubstanceSourceMaterial`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `SubstanceSpecification`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `code`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `_filter`

#### `SupplyDelivery`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `receiver`, `_lastUpdated`, `_security`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `supplier`, `_has`, `_source`, `_id`, `status`

#### `SupplyRequest`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `requester`, `identifier`, `subject`, `_lastUpdated`, `_security`, `_filter`, `_list`, `_profile`, `_tag`, `supplier`, `_has`, `_source`, `_id`, `category`, `status`

#### `Task`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`code`, `subject`, `_lastUpdated`, `focus`, `part-of`, `_list`, `group-identifier`, `based-on`, `patient`, `modified`, `owner`, `requester`, `business-status`, `identifier`, `period`, `performer`, `_security`, `encounter`, `authored-on`, `priority`, `intent`, `_filter`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `status`

#### `TerminologyCapabilities`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `_security`, `description`, `context-type`, `title`, `version`, `url`, `_filter`, `_list`, `context-quantity`, `_profile`, `_tag`, `_has`, `context`, `name`, `publisher`, `_source`, `_id`, `context-type-quantity`, `status`

#### `TestReport`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`identifier`, `_lastUpdated`, `_security`, `tester`, `participant`, `_filter`, `result`, `_list`, `_profile`, `_tag`, `_has`, `_source`, `_id`, `testscript`, `issued`

#### `TestScript`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `testscript-capability`, `context-type`, `title`, `_list`, `context-quantity`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`

#### `ValueSet`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`date`, `code`, `context-type-value`, `_lastUpdated`, `jurisdiction`, `description`, `context-type`, `title`, `reference`, `_list`, `context-quantity`, `context`, `context-type-quantity`, `identifier`, `_security`, `version`, `url`, `expansion`, `_filter`, `_profile`, `_tag`, `_has`, `name`, `publisher`, `_source`, `_id`, `status`

#### `VerificationResult`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`_list`, `_profile`, `_lastUpdated`, `_tag`, `_has`, `_security`, `_source`, `_id`, `target`, `_filter`

#### `VisionPrescription`
- REST interactions：`search-type`, `update`, `vread`, `read`, `patch`, `history-type`, `history-instance`, `delete`, `create`
- Search parameters：`prescriber`, `identifier`, `_lastUpdated`, `datewritten`, `_security`, `encounter`, `_filter`, `_list`, `_profile`, `patient`, `_tag`, `_has`, `_source`, `_id`, `status`

## 5. 回傳格式與必要欄位

- 預設回應 Content-Type（實測）：`application/fhir+json;charset=UTF-8`
- CapabilityStatement `format`：`application/fhir+xml`, `xml`, `application/fhir+json`, `json`, `application/x-turtle`, `ttl`, `html/json`, `html/xml`, `html/turtle`
- Patch 格式：`application/fhir+json`, `application/fhir+xml`, `application/json-patch+json`, `application/xml-patch+xml`
- 錯誤格式：FHIR `OperationOutcome`（見第 6 節實測）

### 專案自訂 Profile 的必要欄位（Phase 1）

- `Patient` (`patient-intake-patient`) 必要路徑：`Patient.identifier`, `Patient.identifier.system`, `Patient.identifier.value`, `Patient.name`, `Patient.gender`
- `Observation` (`patient-intake-observation`) 必要路徑：`Observation.status`, `Observation.code`, `Observation.subject`

## 6. base URL、認證、CORS、pagination、錯誤格式

### Base URL
- dev：`http://localhost:8091/fhir`（`docker-compose.dev.yml`）
- auth：`http://localhost:8090/fhir`（`docker-compose.auth.yml` + oauth2-proxy）

### 認證
- dev：未強制 OAuth/JWT（本機開發便利）
- auth：Keycloak OIDC + OAuth2 Proxy，透過 Bearer Token 驗證

### CORS
- `Access-Control-Allow-Origin`（實測）：`(empty)`
- `Access-Control-Allow-Methods`（實測）：`(empty)`
- 結論：目前未看到明確 CORS header，若前端跨網域部署會卡。

### Pagination
- 實測 `GET /Observation?_count=2`：
  - `entry` 筆數：`2`
  - `link.next`：`True`
  - next URL 範例：`http://localhost:8091/fhir?_getpages=56003c38-6d0b-43ff-9d0c-3329acbd1abe&_getpagesoffset=2&_count=2&_pretty=true&_bundletype=searchset`

### 錯誤格式（OperationOutcome 實測）

```json
{
  "resourceType": "OperationOutcome",
  "issue": [ {
    "severity": "error",
    "code": "processing",
    "diagnostics": "HAPI-2001: Resource Patient/not-exists-xyz is not known"
  } ]
}
```

## 7. 第一階段前端會卡住的缺口（摘要）

- 詳細清單請見：`BACKEND_GAPS_FOR_PHASE1.md`
- 最高優先：
  1. 缺少穩定前端導向 API Facade（目前前端需直接處理大量 FHIR 細節）
  2. 缺少明確 CORS 設定
  3. 缺少統一錯誤碼與錯誤訊息映射（OperationOutcome -> UI）

## 8. Phase 1 後端能力補齊狀態（本次）

- Facade 決策：`提供`（已落地）
  - `GET /api/patients/{id}/intake-summary`
  - `POST /api/patients/intake`
  - `PATCH /api/patients/{id}/intake`
- CORS：已在 Phase 1 facade 層補上（`Access-Control-Allow-Origin` 預設 `*`，可由啟動參數覆蓋）
- OperationOutcome -> UI 錯誤映射：已在 facade 補上（`PATIENT_NOT_FOUND` / `VALIDATION_ERROR` / `UNAUTHORIZED` / `FORBIDDEN` / `SERVER_ERROR` 等）
- 測試資料：已提供 `phase1-patient-001` 與可重複建立 sample payload

相關檔案：
- `scripts/import_ui_server.py`
- `scripts/start-import-ui.ps1`
- `scripts/seed-phase1-test-data.ps1`
- `fhir-model/examples/phase1-intake-create.sample.json`
- `PHASE1_FRONTEND_ENDPOINTS.md`
- `OPERATIONOUTCOME_UI_MAPPING.md`

