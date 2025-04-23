"use client";
import React from "react";
import { title } from "@/components/primitives";
import { Form } from "@heroui/form";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Radio, RadioGroup } from "@heroui/radio";
import { Tooltip } from "@heroui/tooltip";
import { XPred } from "@/components/XPred";
import {
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownSection,
  DropdownItem,
} from "@heroui/dropdown";

export default function Predictor() {
  const [submitted, setSubmitted] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [bmi, setBmi] = React.useState<string>("");
  const [touched, setTouched] = React.useState<{ [key: string]: boolean }>({});
  const [prediction, setPrediction] = React.useState<XPred | null>(null);
  const [errors, setErrors] = React.useState<
    Partial<Record<keyof XPred, string>>
  >({});
  const [generalhealthdropdown, setGeneralHealthDropdown] = React.useState(
    new Set(["Excellent"])
  );
  const [Agedropdown, setAgeDropdown] = React.useState(new Set(["Age18to24"]));
  const [educationdropdown, setEducationDropdown] = React.useState(
    new Set(["Never Attended or Only Kindergarten"])
  );
  const [incomedropdown, setIncomeDropdown] = React.useState(
    new Set(["Less than $10,000"])
  );

  const handleRadioChange = (name: keyof XPred, value: string) => {
    setPrediction((prev) => ({
      ...(prev ?? {}),
      [name]: value === "true" ? true : false,
    }));
  };

  const handleBlur = (fieldName: string) => {
    setTouched((prev) => ({
      ...prev,
      [fieldName]: true,
    }));
  };

  const handleBMIChange = (value: string) => {
    const bmi = parseFloat(value);
    if (isNaN(bmi) || bmi <= 0 || bmi > 200) {
      setPrediction((prev) => ({
        ...(prev ?? {}),
        Underweight: undefined,
        NormalWeight: undefined,
        Overweight: undefined,
        Class1Obesity: undefined,
        Class2Obesity: undefined,
        Class3Obesity: undefined,
      }));
      setErrors((prev) => ({
        ...prev,
        Underweight: "Must be a number between 0 and 200",
      }));
      setBmi(bmi.toString());
    } else {
      setPrediction((prev) => ({
        ...(prev ?? {}),
        Underweight: bmi < 18.5,
        NormalWeight: bmi >= 18.5 && bmi < 25,
        Overweight: bmi >= 25 && bmi < 30,
        Class1Obesity: bmi >= 30 && bmi < 35,
        Class2Obesity: bmi >= 35 && bmi < 40,
        Class3Obesity: bmi >= 40,
      }));
      setBmi(value);
      setErrors((prev) => ({
        ...prev,
        Underweight: undefined,
      }));
    }
  };

  const handleGeneralHealthDropdownChange = (key: string) => {
    setPrediction((prev) => ({
      ...(prev ?? {}),
      ExcellentGeneralHealth: key === "Excellent",
      VeryGoodGeneralHealth: key === "Very Good",
      GoodGeneralHealth: key === "Good",
      FairGeneralHealth: key === "Fair",
      PoorGeneralHealth: key === "Poor",
    }));
    setGeneralHealthDropdown(new Set([key]));
  };

  const handleAgeDropdownChange = (key: string) => {
    setPrediction((prev) => ({
      ...(prev ?? {}),
      Age18to24: key === "Age 18-24",
      Age25to29: key === "Age 25-29",
      Age30to34: key === "Age 30-34",
      Age35to39: key === "Age 35-39",
      Age40to44: key === "Age 40-44",
      Age45to49: key === "Age 45-49",
      Age50to54: key === "Age 50-54",
      Age55to59: key === "Age 55-59",
      Age60to64: key === "Age 60-64",
      Age65to69: key === "Age 65-69",
      Age70to74: key === "Age 70-74",
      Age75to79: key === "Age 75-79",
      Age80Plus: key === "Age 80+",
    }));
    setAgeDropdown(new Set([key]));
  };

  const handleIncomeDropdownChange = (key: string) => {
    setPrediction((prev) => ({
      ...(prev ?? {}),
      EarnLessThan10K: key === "Less than $10,000",
      Earn10Kto14K: key === "$10,000-$14,999",
      Earn15Kto19K: key === "$15,000-$19,999",
      Earn20Kto24K: key === "$20,000-$24,999",
      Earn25Kto34K: key === "$25,000-$34,999",
      Earn35Kto49K: key === "$35,000-$49,999",
      Earn50Kto74K: key === "$50,000-$74,999",
      Earn75korMore: key === "$75,000 or more",
    }));
    setIncomeDropdown(new Set([key]));
  };

  const handleEducationDropdownChange = (key: string) => {
    setPrediction((prev) => ({
      ...(prev ?? {}),
      NeverAttendedOrOnlyKindergarten:
        key === "Never Attended or Only Kindergarten",
      SomeElementary: key === "Some Elementary",
      SomeHighSchool: key === "Some High School",
      GraduatedFromHighSchool: key === "Graduated From High School",
      SomeCollegeOrTechnicalSchool: key === "Some College or Technical School",
      GraduatedFromCollege: key === "Graduated From College",
    }));
    setEducationDropdown(new Set([key]));
  };

  const onSubmit = (e: any) => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(e.currentTarget));
  };

  return (
    <>
      <div className="text-center justify-self-center mb-10 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent text-6xl font-bold drop-shadow-[0_0_10px_rgba(255,255,255,0.3)] animate-pulse hover:scale-105 transition-all duration-300 ease-in-out cursor-pointer">
        <span>Prediction&nbsp;</span>
      </div>
      <Form
        className="w-full grid sm:grid-cols-4 md:grid-cols-8 mt-5 gap-8 border-2 border-default-200 rounded-lg p-4"
        onSubmit={onSubmit}
      >
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Do you have High Blood Pressure?"
            value={
              prediction?.HighBP !== undefined ? String(prediction.HighBP) : ""
            }
            onValueChange={(value) => handleRadioChange("HighBP", value)}
            isRequired
            name="HighBloodPressure"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Do you have High Cholesterol?"
            value={
              prediction?.HighChol !== undefined
                ? String(prediction.HighChol)
                : ""
            }
            isRequired
            onValueChange={(value) => handleRadioChange("HighChol", value)}
            name="HighCholesterol"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Have you checked your Cholesterol in the last 5 years?"
            isRequired
            value={
              prediction?.CholCheck !== undefined
                ? String(prediction.CholCheck)
                : ""
            }
            name="CholCheck"
            onValueChange={(value) => handleRadioChange("CholCheck", value)}
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <Input
            isRequired
            className="max-w-xs"
            label="Body Mass Index (BMI)"
            name="BMI"
            value={bmi}
            onValueChange={(value) => {
              handleBMIChange(value);
            }}
            errorMessage={
              errors.Underweight && bmi !== ""
                ? errors.Underweight
                : bmi === "" && touched.BMI
                  ? "This field is required"
                  : undefined
            }
            isInvalid={!!errors.Underweight || (bmi === "" && touched.BMI)}
            type="number"
            labelPlacement="outside"
            placeholder="Enter your BMI"
            onBlur={() => handleBlur("BMI")}
            classNames={{
              label: "!text-default-500",
            }}
          />
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Are you a smoker (Smoked atleast 100 cigarettes)?"
            isRequired
            name="Smoker"
            value={
              prediction?.Smoker !== undefined ? String(prediction.Smoker) : ""
            }
            onValueChange={(value) => handleRadioChange("Smoker", value)}
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Have you ever had a stroke?"
            value={
              prediction?.Stroke !== undefined ? String(prediction.Stroke) : ""
            }
            isRequired
            name="Stroke"
            onValueChange={(value) => handleRadioChange("Stroke", value)}
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Do you have Coronary Heart Disease (CHD) or myocardial infraction (MI)?"
            value={
              prediction?.HeartDisease !== undefined
                ? String(prediction.HeartDisease)
                : ""
            }
            isRequired
            name="HeartDisease"
            onValueChange={(value) => handleRadioChange("HeartDisease", value)}
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Are you Physically Active (Past 30 days)?"
            value={
              prediction?.PhysicalActivity !== undefined
                ? String(prediction.PhysicalActivity)
                : ""
            }
            onValueChange={(value) =>
              handleRadioChange("PhysicalActivity", value)
            }
            isRequired
            name="PhysActive"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Do you consume Fruits daily?"
            value={
              prediction?.Fruits !== undefined ? String(prediction.Fruits) : ""
            }
            onValueChange={(value) => handleRadioChange("Fruits", value)}
            isRequired
            name="Fruits"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Do you consume Vegetables daily?"
            value={
              prediction?.Veggies !== undefined
                ? String(prediction.Veggies)
                : ""
            }
            onValueChange={(value) => handleRadioChange("Veggies", value)}
            isRequired
            name="Veggies"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Are you a Heavy Drinker (adult men having more than 14 drinks per week and adult women having more than 7 drinks per week)?"
            value={
              prediction?.HvyAlcoholConsump !== undefined
                ? String(prediction.HvyAlcoholConsump)
                : ""
            }
            onValueChange={(value) =>
              handleRadioChange("HvyAlcoholConsump", value)
            }
            isRequired
            name="HeavyAlcohol"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Do you have Any Healthcare (health insurance, prepaid plans such as HMO, etc)?"
            value={
              prediction?.AnyHealthcare !== undefined
                ? String(prediction.AnyHealthcare)
                : ""
            }
            onValueChange={(value) => handleRadioChange("AnyHealthcare", value)}
            isRequired
            name="AnyHealthcare"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Was there a time in the past 12 months when you needed to see a doctor but could not because of cost?"
            value={
              prediction?.NoDocbcCost !== undefined
                ? String(prediction.NoDocbcCost)
                : ""
            }
            onValueChange={(value) => handleRadioChange("NoDocbcCost", value)}
            isRequired
            name="NoDocCost"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <label
            htmlFor="general-health-dropdown"
            className="mb-2 text-sm font-medium text-default-500"
          >
            General Health
          </label>
          <Dropdown>
            <DropdownTrigger>
              <Button
                id="general-health-dropdown"
                className="capitalize"
                variant="bordered"
              >
                {Array.from(generalhealthdropdown)[0]}
              </Button>
            </DropdownTrigger>
            <DropdownMenu
              disallowEmptySelection
              aria-label="General health selection"
              selectedKeys={generalhealthdropdown}
              selectionMode="single"
              variant="flat"
              onSelectionChange={(keys) => {
                const selected = Array.from(keys)[0];
                handleGeneralHealthDropdownChange(selected as string);
              }}
            >
              <DropdownItem key="Excellent">Excellent</DropdownItem>
              <DropdownItem key="Very Good">Very Good</DropdownItem>
              <DropdownItem key="Good">Good</DropdownItem>
              <DropdownItem key="Fair">Fair</DropdownItem>
              <DropdownItem key="Poor">Poor</DropdownItem>
            </DropdownMenu>
          </Dropdown>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Have you felt Mentally Unwell for at least 1 day last month"
            value={
              prediction?.MentallyHealthy !== undefined
                ? String(prediction.MentallyHealthy)
                : ""
            }
            isRequired
            onValueChange={(value) =>
              handleRadioChange("MentallyHealthy", value)
            }
            name="MentallyHealthy"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Have you felt Physically Unwell for at least 1 day last month?"
            value={
              prediction?.PhysicallyHealthy !== undefined
                ? String(prediction.PhysicallyHealthy)
                : ""
            }
            isRequired
            onValueChange={(value) =>
              handleRadioChange("PhysicallyHealthy", value)
            }
            name="PhysicallyHealthy"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Do you have serious Diffuculty Walking or Climbing Stairs?"
            value={
              prediction?.DiffWalk !== undefined
                ? String(prediction.DiffWalk)
                : ""
            }
            onValueChange={(value) => handleRadioChange("DiffWalk", value)}
            isRequired
            name="DiffWalk"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Yes</Radio>
            <Radio value="false">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="secondary"
            label="Sex"
            value={prediction?.Sex !== undefined ? String(prediction.Sex) : ""}
            onValueChange={(value) => handleRadioChange("Sex", value)}
            isRequired
            name="Sex"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="true">Male</Radio>
            <Radio value="false">Female</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <label
            htmlFor="age-dropdown"
            className="mb-2 text-sm font-medium text-default-500"
          >
            Age
          </label>
          <Dropdown>
            <DropdownTrigger>
              <Button
                id="age-dropdown"
                className="capitalize"
                variant="bordered"
              >
                {Array.from(Agedropdown)[0]}
              </Button>
            </DropdownTrigger>
            <DropdownMenu
              disallowEmptySelection
              aria-label="General health selection"
              selectedKeys={Agedropdown}
              selectionMode="single"
              variant="flat"
              onSelectionChange={(keys) => {
                const selected = Array.from(keys)[0];
                handleAgeDropdownChange(selected as string);
              }}
            >
              <DropdownItem key="Age 18-24">Age 18-24</DropdownItem>
              <DropdownItem key="Age 25-29">Age 25-29</DropdownItem>
              <DropdownItem key="Age 30-34">Age 30-34</DropdownItem>
              <DropdownItem key="Age 35-39">Age 35-39</DropdownItem>
              <DropdownItem key="Age 40-44">Age 40-44</DropdownItem>
              <DropdownItem key="Age 45-49">Age 45-49</DropdownItem>
              <DropdownItem key="Age 50-54">Age 50-54</DropdownItem>
              <DropdownItem key="Age 55-59">Age 55-59</DropdownItem>
              <DropdownItem key="Age 60-64">Age 60-64</DropdownItem>
              <DropdownItem key="Age 65-69">Age 65-69</DropdownItem>
              <DropdownItem key="Age 70-74">Age 70-74</DropdownItem>
              <DropdownItem key="Age 75-79">Age 75-79</DropdownItem>
              <DropdownItem key="Age 80+">Age 80+</DropdownItem>
            </DropdownMenu>
          </Dropdown>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <label
            htmlFor="education-dropdown"
            className="mb-2 text-sm font-medium text-default-500"
          >
            Education
          </label>
          <Dropdown>
            <DropdownTrigger>
              <Button
                id="education-dropdown"
                className="capitalize"
                variant="bordered"
              >
                {Array.from(educationdropdown)[0]}
              </Button>
            </DropdownTrigger>
            <DropdownMenu
              disallowEmptySelection
              aria-label="General health selection"
              selectedKeys={educationdropdown}
              selectionMode="single"
              variant="flat"
              onSelectionChange={(keys) => {
                const selected = Array.from(keys)[0];
                handleEducationDropdownChange(selected as string);
              }}
            >
              <DropdownItem key="Never Attended or Only Kindergarten">
                Never Attended or Only Kindergarten
              </DropdownItem>
              <DropdownItem key="Some Elementary">Some Elementary</DropdownItem>
              <DropdownItem key="Some High School">
                Some High School
              </DropdownItem>
              <DropdownItem key="Graduated From High School">
                Graduated From High School
              </DropdownItem>
              <DropdownItem key="Some College or Technical School">
                Some College or Technical School
              </DropdownItem>
              <DropdownItem key="Graduated From College">
                Graduated From College
              </DropdownItem>
            </DropdownMenu>
          </Dropdown>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <label
            htmlFor="income-dropdown"
            className="mb-2 text-sm font-medium text-default-500"
          >
            Income
          </label>
          <Dropdown>
            <DropdownTrigger>
              <Button
                id="income-dropdown"
                className="capitalize"
                variant="bordered"
              >
                {Array.from(incomedropdown)[0]}
              </Button>
            </DropdownTrigger>
            <DropdownMenu
              disallowEmptySelection
              aria-label="General health selection"
              selectedKeys={incomedropdown}
              selectionMode="single"
              variant="flat"
              onSelectionChange={(keys) => {
                const selected = Array.from(keys)[0];
                handleIncomeDropdownChange(selected as string);
              }}
            >
              <DropdownItem key="Less than $10,000">
                Less than $10,000
              </DropdownItem>
              <DropdownItem key="$10,000-$14,999">$10,000-$14,999</DropdownItem>
              <DropdownItem key="$15,000-$19,999">$15,000-$19,999</DropdownItem>
              <DropdownItem key="$20,000-$24,999">$20,000-$24,999</DropdownItem>
              <DropdownItem key="$25,000-$34,999">$25,000-$34,999</DropdownItem>
              <DropdownItem key="$35,000-$49,999">$35,000-$49,999</DropdownItem>
              <DropdownItem key="$50,000-$74,999">$50,000-$74,999</DropdownItem>
              <DropdownItem key="$75,000 or more">$75,000 or more</DropdownItem>
            </DropdownMenu>
          </Dropdown>
        </div>
        <div className="sm:col-span-4 md:col-span-8 flex flex-col items-center justify-center mt-4">
          <Button
            type="submit"
            variant="bordered"
            className="w-full justify-self-center bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-black hover:text-white"
          >
            Submit
          </Button>
        </div>
      </Form>
    </>
  );
}
