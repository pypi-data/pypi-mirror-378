from pandera import DataFrameModel, Field as PanderaField, Check
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from enum import Enum


class GetWorkerSchema(DataFrameModel):
    # Required fields
    name: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 40}, alias="Name")
    firstname: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 25}, alias="Firstname")

    # Optional fields with specific validations
    inss: Optional[float] = PanderaField(nullable=True, ge=0.0, le=99999999999.0, alias="INSS")
    sex: Optional[str] = PanderaField(nullable=True, isin=['M', 'F'], alias="Sex")
    birthdate: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Birthdate")
    birthplace_zip_code: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 12}, alias="BirthplaceZIPCode")
    birthplace: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 30}, alias="Birthplace")
    birthplace_country: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default='00150', alias="BirthplaceCountry")
    nationality: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default='00150', alias="Nationality")
    language: Optional[str] = PanderaField(nullable=True, isin=['N', 'F', 'D', 'E'], alias="Language")
    pay_way: Optional[str] = PanderaField(nullable=True, isin=['Cash', 'Transfer', 'Electronic', 'AssignmentList'], alias="PayWay")
    bank_account: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 45}, alias="BankAccount")
    bic_code: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15}, alias="BICCode")
    id: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15}, alias="ID")
    id_type: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 3}, alias="IDType")
    id_valid_until: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="IDValidUntil")
    driver_license: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15}, alias="DriverLicense")
    driver_category: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 2}, alias="DriverCategory")
    number_plate: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, alias="NumberPlate")
    fuel_card: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 20}, alias="FuelCard")
    education: Optional[str] = PanderaField(nullable=True, isin=[
        'Basic', 'LowerSecondary', 'HigherSecondary', 'NotUniversity',
        'University', 'Secondary1Degree', 'Secondary2Degree', 'Secondary3Degree', 'Unknown'
    ], alias="Education")
    profession: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 50}, alias="Profession")
    e_health_insurance: Optional[int] = PanderaField(nullable=True, ge=0, le=9999, alias="EHealthInsurance")
    e_health_insurance_reference: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 20}, alias="EHealthInsuranceReference")
    accident_insurance: Optional[int] = PanderaField(nullable=True, ge=0, le=9999, alias="AccidentInsurance")
    medical_center: Optional[int] = PanderaField(nullable=True, ge=0, le=9999, alias="MedicalCenter")
    medical_center_reference: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15}, alias="MedicalCenterReference")
    external_id: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 50}, alias="ExternalID")
    interim_from: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="InterimFrom")
    interim_to: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="InterimTo")
    travel_expenses: Optional[str] = PanderaField(nullable=True, isin=[
        'PublicTransportTrain', 'OwnTransport', 'PublicTransportOther', 'Bicycle', 'None'
    ], alias="TravelExpenses")
    type_of_travel_expenses: Optional[str] = PanderaField(nullable=True, isin=[
        'Other', 'PublicCommonTransport', 'OrganisedCommonTransport'
    ], alias="TypeOfTravelExpenses")
    salary_code_travel_expenses: Optional[int] = PanderaField(nullable=True, ge=1, le=9999, alias="SalaryCodeTravelExpenses")
    main_division: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, alias="MainDivision")

    class Config:
        strict = True
        coerce = True


class ExistEnum(str, Enum):
    NO = 'N'
    YES = 'Y'


class CareerBreakKindEnum(str, Enum):
    FULLTIME = 'Fulltime'
    PART_TIME_ONE_FIFTH = 'PartTimeOneFifth'
    PART_TIME_ONE_QUARTER = 'PartTimeOneQuarter'
    PART_TIME_ONE_THIRD = 'PartTimeOneThird'
    PART_TIME_HALF = 'PartTimeHalf'
    PART_TIME_THREE_FIFTHS = 'PartTimeThreeFifths'
    PART_TIME_ONE_TENTH = 'PartTimeOneTenth'


class CareerBreakReasonEnum(str, Enum):
    PALLIATIVE_CARE = 'PalliativeCare'
    SERIOUSLY_ILL = 'SeriouslyIll'
    OTHER = 'Other'
    PARENTAL_LEAVE = 'ParentalLeave'
    CRISIS = 'Crisis'
    FAMILY_CARE = 'FamilyCare'
    END_OF_CAREER = 'EndOfCareer'
    SICK_CHILD = 'SickChild'
    FAMILY_CARE_CORONA = 'FamilyCareCorona'
    CHILD_CARE_UNDER_8 = 'ChildCareUnder8'
    CHILD_CARE_HANDICAP_UNDER_21 = 'ChildCareHandicapUnder21'
    CERTIFIED_TRAINING = 'CertifiedTraining'


class ContractTypeEnum(str, Enum):
    FULLTIME = 'Fulltime'
    PART_TIME = 'PartTime'


class CivilStatusEnum(str, Enum):
    SINGLE = 'Single'
    MARRIED = 'Married'
    WIDOW = 'Widow'
    DIVORCED = 'Divorced'
    SEPARATED = 'Separated'
    COHABITATION = 'Cohabitation'
    LIVE_TOGETHER = 'LiveTogether'


class SpouseIncomeEnum(str, Enum):
    WITH_INCOME = 'WithIncome'
    WITHOUT_INCOME = 'WithoutIncome'
    PROFF_INCOME_LESS_THAN_235 = 'ProffIncomeLessThan235'
    PROFF_INCOME_LESS_THAN_141 = 'ProffIncomeLessThan141'
    PROFF_INCOME_LESS_THAN_469 = 'ProffIncomeLessThan469'


class SpouseProfessionEnum(str, Enum):
    HANDWORKER = 'Handworker'
    SERVANT = 'Servant'
    EMPLOYEE = 'Employee'
    SELF_EMPLOYED = 'SelfEmployed'
    MINER = 'Miner'
    SAILOR = 'Sailor'
    CIVIL_SERVANT = 'CivilServant'
    OTHER = 'Other'
    NIL = 'Nil'


class TaxCalculationEnum(str, Enum):
    NORMAL = 'Normal'
    CONVERSION_PT = 'ConversionPT'
    FISC_VOL_AMOUNT = 'FiscVolAmount'
    FISC_VOL_PERCENT = 'FiscVolPercent'
    AMOUNT = 'Amount'
    PERCENT = 'Percent'
    PERCENT_NORMAL = 'PercentNormal'
    NON_RESIDENT = 'NonResident'
    NO_CITY = 'NoCity'
    NO_TAX = 'NoTax'
    YOUNGER = 'Younger'
    NORMAL_PLUS = 'NormalPlus'
    TRAINER = 'Trainer'
    NORMAL_MIN_PERC = 'NormalMinPerc'
    NORMAL_MIN_AMOUNT = 'NormalMinAmount'


class CareerBreakDefinition(BaseModel):
    Exist: ExistEnum
    Kind: Optional[CareerBreakKindEnum] = None
    Reason: Optional[CareerBreakReasonEnum] = None
    OriginallyContractType: Optional[ContractTypeEnum] = None
    WeekhoursWorkerBefore: Optional[float] = None
    WeekhoursEmployerBefore: Optional[float] = None


class CertainWorkDefinition(BaseModel):
    Exist: ExistEnum
    Description: Optional[str] = Field(None, min_length=0, max_length=250)


class Address(BaseModel):
    Startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Street: str = Field(..., min_length=0, max_length=100)
    HouseNumber: str = Field(..., min_length=0, max_length=10)
    PostBox: Optional[str] = Field(None, min_length=0, max_length=5)
    ZIPCode: str = Field(..., min_length=0, max_length=12)
    City: str = Field(..., min_length=0, max_length=30)
    Country: str = Field(default='00150', min_length=5, max_length=5, pattern=r'^[0-9]*$')
    Distance: Optional[float] = Field(None, ge=0.0, le=99999.9)


class CommunicationModel(BaseModel):
    communication_type: Literal['None', 'Phone', 'GSM', 'Email', 'PrivatePhone',
    'Fax', 'InternalPhone', 'PrivateEmail', 'GSMEntreprise',
    'Website']
    value: str = Field(..., min_length=0, max_length=100, alias="Value")
    contact_person: Optional[str] = Field(None, min_length=0, max_length=100, alias="ContactPerson")


EmploymentStatusType = Literal['Workman', 'Employee', 'Director']
ContractLiteral = Literal[
    'Usually', 'FlexiVerbal', 'FlexiWritten', 'FlexiLiable', 'Sportsperson',
    'Housekeeper', 'Servant', 'Agriculture', 'Homework', 'HomeworkChildcare',
    'Physician', 'PhysicianTraining', 'PhysicianIndependant', 'ApprenticeFlemisch',
    'ApprenticeFrench', 'ApprenticeGerman', 'ApprenticeManager', 'ApprenticeIndustrial',
    'ApprenticeSocio', 'ApprenticeBio', 'ApprenticeAlternating', 'EarlyRetirement',
    'EarlyRetirementPartTime', 'FreeNOSS', 'FreeNOSSManager', 'FreeNOSSOther',
    'FreeNOSSSportingEvent', 'FreeNOSSHelper', 'FreeNOSSSocio', 'FreeNOSSEducation',
    'FreeNOSSSpecialCultures', 'FreeNOSSVolunteer', 'Horeca', 'HorecaExtraHourLiable',
    'HorecaExtraDayLiable', 'HorecaExtraHourForfait', 'HorecaExtraDayForfait',
    'HorecaFlexiVerbal', 'HorecaFlexiWritten', 'HorecaFlexiLiable', 'Construction',
    'ConstructionAlternating', 'ConstructionApprenticeYounger', 'ConstructionApprentice',
    'ConstructionGodfather', 'JobTrainingIBO', 'JobTrainingSchool', 'JobTrainingVDAB',
    'JobTrainingLiberalProfession', 'JobTrainingEntry', 'JobTrainingPFIWa',
    'JobTrainingABO', 'JobTrainingPFIBx', 'JobTrainingBIO', 'JobTrainingAlternating',
    'JobTrainingDisability', 'NonProfitRiziv', 'NonProfitGesco', 'NonProfitDAC',
    'NonProfitPrime', 'NonProfitLowSkilled', 'Artist', 'ArtistWithContract',
    'ArtistWithoutContract', 'Transport', 'TransportNonMobile', 'TransportGarage',
    'Aircrew', 'AircrewPilot', 'AircrewCabinCrew', 'Interim', 'InterimTemporary',
    'InterimsPermanent', 'External', 'ExternalApplicant', 'ExternalSubcontractor',
    'ExternalAgentIndependant', 'ExternalExtern', 'ExternalIntern', 'ExternalLegalPerson',
    'SalesRepresentative', 'SportsTrainer'
]


class Contract(BaseModel):
    startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    employment_status: Optional[EmploymentStatusType] = None
    contract: Optional[ContractLiteral] = None
    career_break: Optional[CareerBreakDefinition] = None
    certain_work: Optional[CertainWorkDefinition] = None


class FamilyStatus(BaseModel):
    startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    civil_status: Optional[CivilStatusEnum] = None
    worker_handicapped: Optional[ExistEnum] = None
    worker_single_with_children: Optional[ExistEnum] = None
    spouse_with_income: Optional[SpouseIncomeEnum] = None
    spouse_handicapped: Optional[ExistEnum] = None
    spouse_name: Optional[str] = Field(None, min_length=0, max_length=40)
    spouse_firstname: Optional[str] = Field(None, min_length=0, max_length=25)
    spouse_inss: Optional[float] = Field(None, ge=0.0, le=99999999999.0)
    spouse_sex: Optional[Literal['M', 'F']] = None
    spouse_birthdate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    spouse_profession: Optional[SpouseProfessionEnum] = None
    spouse_birthplace: Optional[str] = Field(None, min_length=0, max_length=30)
    children_at_charge: Optional[int] = Field(None, ge=0, le=99)
    children_handicapped: Optional[int] = Field(None, ge=0, le=99)
    others_at_charge: Optional[int] = Field(None, ge=0, le=99)
    others_handicapped: Optional[int] = Field(None, ge=0, le=99)
    others_65_at_charge: Optional[int] = Field(None, ge=0, le=99)
    others_65_handicapped: Optional[int] = Field(None, ge=0, le=99)
    child_benefit_institution: Optional[int] = Field(None, ge=0, le=9999)
    child_benefit_reference: Optional[str] = Field(None, min_length=0, max_length=15)
    weddingdate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')


class TaxModel(BaseModel):
    startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    tax_calculation: TaxCalculationEnum
    value: Optional[float] = Field(None, ge=0.0, le=9999999999.0, alias="Value")


class ReplacementModel(BaseModel):
    worker_number: int = Field(..., ge=1, le=9999999, alias="WorkerNumber")
    startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    percentage: Optional[float] = Field(None, ge=0.0, le=100.0, alias="Percentage")


class PostWorkerSchema(BaseModel):
    # Required fields
    worker_number: int = Field(..., ge=1, le=9999999, alias="WorkerNumber")
    name: str = Field(..., min_length=0, max_length=40, alias="Name")
    firstname: str = Field(..., min_length=0, max_length=25, alias="Firstname")

    # Optional basic fields
    initial: Optional[str] = Field(None, min_length=1, max_length=1, alias="Initial")
    inss: Optional[float] = Field(None, ge=0.0, le=99999999999.0, alias="INSS")
    sex: Optional[Literal['M', 'F']] = None
    birthdate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Birthdate")
    birthplace_zip_code: Optional[str] = Field(None, min_length=0, max_length=12, alias="BirthplaceZIPCode")
    birthplace: Optional[str] = Field(None, min_length=0, max_length=30, alias="Birthplace")
    birthplace_country: Optional[str] = Field(default='00150', min_length=5, max_length=5, pattern=r'^[0-9]*$', alias="BirthplaceCountry")
    nationality: Optional[str] = Field(default='00150', min_length=5, max_length=5, pattern=r'^[0-9]*$', alias="Nationality")
    language: Optional[Literal['N', 'F', 'D', 'E']] = None
    pay_way: Optional[Literal['Cash', 'Transfer', 'Electronic', 'AssignmentList']] = None
    bank_account: Optional[str] = Field(None, min_length=0, max_length=45, alias="BankAccount")
    bic_code: Optional[str] = Field(None, min_length=0, max_length=15, alias="BICCode")
    id: Optional[str] = Field(None, min_length=0, max_length=15, alias="ID")
    id_type: Optional[str] = Field(None, min_length=0, max_length=3, alias="IDType")
    id_valid_until: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="IDValidUntil")
    driver_license: Optional[str] = Field(None, min_length=0, max_length=15, alias="DriverLicense")
    driver_category: Optional[str] = Field(None, min_length=0, max_length=2, alias="DriverCategory")
    number_plate: Optional[str] = Field(None, min_length=0, max_length=10, alias="NumberPlate")
    fuel_card: Optional[str] = Field(None, min_length=0, max_length=20, alias="FuelCard")
    education: Optional[Literal[
        'Basic', 'LowerSecondary', 'HigherSecondary', 'NotUniversity',
        'University', 'Secondary1Degree', 'Secondary2Degree', 'Secondary3Degree', 'Unknown'
    ]] = None
    profession: Optional[str] = Field(None, min_length=0, max_length=50, alias="Profession")
    e_health_insurance: Optional[int] = Field(None, ge=0, le=9999, alias="EHealthInsurance")
    e_health_insurance_reference: Optional[str] = Field(None, min_length=0, max_length=20, alias="EHealthInsuranceReference")
    accident_insurance: Optional[int] = Field(None, ge=0, le=9999, alias="AccidentInsurance")
    medical_center: Optional[int] = Field(None, ge=0, le=9999, alias="MedicalCenter")
    medical_center_reference: Optional[str] = Field(None, min_length=0, max_length=15, alias="MedicalCenterReference")
    external_id: Optional[str] = Field(None, min_length=0, max_length=50, alias="ExternalID")
    interim_from: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="InterimFrom")
    interim_to: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="InterimTo")
    travel_expenses: Optional[Literal[
        'PublicTransportTrain', 'OwnTransport', 'PublicTransportOther',
        'Bicycle', 'None'
    ]] = None
    type_of_travel_expenses: Optional[Literal[
        'Other', 'PublicCommonTransport', 'OrganisedCommonTransport'
    ]] = None
    salary_code_travel_expenses: Optional[int] = Field(None, ge=1, le=9999, alias="SalaryCodeTravelExpenses")

    # Required nested schemas
    address: List[Address]
    family_status: List[FamilyStatus]
    contract: List[Contract]

    # Optional nested schemas
    communication: Optional[List[CommunicationModel] | None] = None
    tax: Optional[List[TaxModel] | None] = None
    replacement: Optional[List[ReplacementModel] | None] = None
