export interface XPred {
    HighBP?: boolean;
    HighChol?: boolean;
    CholCheck?: boolean;
    Smoker?: boolean;
    Stroke?: boolean;
    HeartDisease?: boolean;
    PhysicalActivity?: boolean;
    Fruits?: boolean;
    Veggies?: boolean;
    HvyAlcoholConsump?: boolean;
    AnyHealthcare?: boolean;
    NoDocbcCost?: boolean;
    DiffWalk?: boolean;
    Sex?: boolean;
    Underweight?: boolean;
    NormalWeight?: boolean;
    Overweight?: boolean;
    Class1Obesity?: boolean;
    Class2Obesity?: boolean;
    Class3Obesity?: boolean;
    ExcellentGeneralHealth?: boolean;
    VeryGoodGeneralHealth?: boolean;
    GoodGeneralHealth?: boolean;
    FairGeneralHealth?: boolean;
    PoorGeneralHealth?: boolean;
    MentallyHealthy?: boolean;
    PhysicallyHealthy?: boolean;
    Age18to24?: boolean;
    Age25to29?: boolean;
    Age30to34?: boolean;
    Age35to39?: boolean;
    Age40to44?: boolean;
    Age45to49?: boolean;
    Age50to54?: boolean;
    Age55to59?: boolean;
    Age60to64?: boolean;
    Age65to69?: boolean;
    Age70to74?: boolean;
    Age75to79?: boolean;
    Age80Plus?: boolean;
    NeverAttendedOrOnlyKindergarten?: boolean;
    SomeElementary?: boolean;
    SomeHighSchool?: boolean;
    GraduatedFromHighSchool?: boolean;
    SomeCollegeOrTechnicalSchool?: boolean;
    GraduatedFromCollege?: boolean;
    EarnLessThan10K?: boolean;
    Earn10Kto14K?: boolean;
    Earn15Kto19K?: boolean;
    Earn20Kto24K?: boolean;
    Earn25Kto34K?: boolean;
    Earn35Kto49K?: boolean;
    Earn50Kto74K?: boolean;  
    Earn75korMore?: boolean;
}

export interface XPredResult {
    prediction?: string;
    probability?: number;
}

export function orderXPredObject(obj: Record<string, any>): XPred {
    const ordered: XPred = {};

    // Define the keys in the order they appear in the XPred interface
    const keysOrder: (keyof XPred)[] = [
        "HighBP", "HighChol", "CholCheck", "Smoker", "Stroke", "HeartDisease", "PhysicalActivity", "Fruits", "Veggies", "HvyAlcoholConsump", "AnyHealthcare", "NoDocbcCost", "DiffWalk", "Sex", "Underweight", "NormalWeight", "Overweight", "Class1Obesity", "Class2Obesity", "Class3Obesity", "ExcellentGeneralHealth", "VeryGoodGeneralHealth", "GoodGeneralHealth", "FairGeneralHealth", "PoorGeneralHealth", "MentallyHealthy", "PhysicallyHealthy", "Age18to24", "Age25to29", "Age30to34", "Age35to39", "Age40to44", "Age45to49", "Age50to54", "Age55to59", "Age60to64", "Age65to69", "Age70to74", "Age75to79", "Age80Plus", "NeverAttendedOrOnlyKindergarten", "SomeElementary", "SomeHighSchool", "GraduatedFromHighSchool", "SomeCollegeOrTechnicalSchool", "GraduatedFromCollege", "EarnLessThan10K", "Earn10Kto14K", "Earn15Kto19K", "Earn20Kto24K", "Earn25Kto34K", "Earn35Kto49K", "Earn50Kto74K", "Earn75korMore"
    ];

    // Iterate over the keys in the defined order
    keysOrder.forEach((key) => {
        if (key in obj) {
            ordered[key] = obj[key];
        }
    });

    return ordered;
}