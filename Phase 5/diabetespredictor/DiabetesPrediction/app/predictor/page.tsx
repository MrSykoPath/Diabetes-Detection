"use client";
import React from "react";
import { title } from "@/components/primitives";
import { Form } from "@heroui/form";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Radio, RadioGroup } from "@heroui/radio";
import { Tooltip } from "@heroui/tooltip";

export default function Predictor() {
  const [submitted, setSubmitted] = React.useState(null);

  const onSubmit = (e: any) => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(e.currentTarget));
  };

  return (
    <>
      <div className="text-center justify-self-center">
        <span
          className={
            title({ color: "cyan" }) +
            " underline decoration-indigo-500 underline-offset-8"
          }
        >
          Prediction&nbsp;
        </span>
      </div>
      <Form
        className="w-full grid sm:grid-cols-4 md:grid-cols-8 mt-5 gap-8 border-2 border-default-200 rounded-lg p-4"
        onSubmit={onSubmit}
      >
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Do you have High Blood Pressure?"
            isRequired
            defaultValue={"False"}
            name="HighBloodPressure"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Do you have High Cholesterol?"
            isRequired
            defaultValue={"False"}
            name="HighCholesterol"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Have you checked your Cholesterol in the last 5 years?"
            isRequired
            defaultValue={"False"}
            name="CholCheck"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <Input
            isRequired
            className="max-w-xs"
            defaultValue="0.0"
            label="Body Mass Index (BMI)"
            name="BMI"
            errorMessage="This field is required"
            type="number"
            labelPlacement="outside"
            placeholder="Enter your BMI"
            classNames={{
              label: "!text-default-500",
            }}
          />
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Are you a smoker (Smoked atleast 100 cigarettes)?"
            isRequired
            defaultValue={"False"}
            name="Smoker"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Have you ever had a stroke?"
            isRequired
            defaultValue={"False"}
            name="Stroke"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Do you have Coronary Heart Disease (CHD) or myocardial infraction (MI)?"
            isRequired
            defaultValue={"False"}
            name="HeartDisease"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Are you Physically Active (Past 30 days)?"
            isRequired
            defaultValue={"False"}
            name="PhysActive"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Do you consume Fruits daily?"
            isRequired
            defaultValue={"False"}
            name="Fruits"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Do you consume Vegetables daily?"
            isRequired
            defaultValue={"False"}
            name="Veggies"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Are you a Heavy Drinker (adult men having more than 14 drinks per week and adult women having more than 7 drinks per week)?"
            isRequired
            defaultValue={"False"}
            name="HeavyAlcohol"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Do you have Any Healthcare (health insurance, prepaid plans such as HMO, etc)?"
            isRequired
            defaultValue={"False"}
            name="AnyHealthcare"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Was there a time in the past 12 months when you needed to see a doctor but could not because of cost?"
            isRequired
            defaultValue={"False"}
            name="NoDocCost"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <Input
            isRequired
            className="max-w-xs"
            defaultValue="0.0"
            label="General Health (1-5) 1 = excellent 2 = very good 3 = good 4 = fair 5 = poor"
            name="GenHealth"
            errorMessage="This field is required"
            type="number"
            labelPlacement="outside"
            placeholder="Enter your General Health"
            classNames={{
              label: "!text-default-500",
            }}
          />
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <Input
            isRequired
            className="max-w-xs"
            defaultValue="0.0"
            label="Mental Health (1-30) 1 = Best 30 = Worst"
            name="MentHealth"
            errorMessage="This field is required"
            type="number"
            labelPlacement="outside"
            placeholder="Enter your Mental Health"
            classNames={{
              label: "!text-default-500",
            }}
          />
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <Input
            isRequired
            className="max-w-xs"
            defaultValue="0.0"
            label="Physical Health (1-30) 1 = Best 30 = Worst"
            name="PhysHealth"
            errorMessage="This field is required"
            type="number"
            labelPlacement="outside"
            placeholder="Enter your Physical Health"
            classNames={{
              label: "!text-default-500",
            }}
          />
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Do you have serious Diffuculty Walking or Climbing Stairs?"
            isRequired
            defaultValue={"False"}
            name="DiffWalk"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Yes</Radio>
            <Radio value="False">No</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <RadioGroup
            color="warning"
            label="Sex "
            isRequired
            defaultValue={"False"}
            name="Sex"
            errorMessage="This field is required"
            classNames={{
              label: "max-w-xs",
            }}
          >
            <Radio value="True">Male</Radio>
            <Radio value="False">Female</Radio>
          </RadioGroup>
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <Input
            isRequired
            className="max-w-xs"
            defaultValue="0.0"
            label="Age (in years)"
            name="Age"
            errorMessage="This field is required"
            type="number"
            labelPlacement="outside"
            placeholder="Enter your Age"
            classNames={{
              label: "!text-default-500",
            }}
          />
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <Input
            isRequired
            className="max-w-xs"
            defaultValue="0.0"
            label={
              <div className="flex items-center gap-1">
                Education Level *
                <Tooltip
                  content={
                    <div className="text-sm max-w-xs">
                      <p>Scale 1–6:</p>
                      <p>1 = Never attended school or only kindergarten</p>
                      <p>2 = Grades 1–8 (Elementary)</p>
                      <p>3 = Grades 9–11 (Some high school)</p>
                      <p>4 = Grade 12 or GED (High school graduate)</p>
                      <p>5 = College 1–3 years (Some college)</p>
                      <p>6 = College 4+ years (College graduate)</p>
                    </div>
                  }
                  showArrow
                  placement="right"
                >
                  <span className="text-primary cursor-pointer text-sm">ⓘ</span>
                </Tooltip>
              </div>
            }
            name="Education"
            errorMessage="This field is required"
            type="number"
            labelPlacement="outside"
            placeholder="Enter your Education Level"
            classNames={{
              label: "!text-default-500",
            }}
          />
        </div>
        <div className="sm:col-span-2 flex flex-col">
          <Input
            isRequired
            className="max-w-xs"
            defaultValue="0.0"
            label={
              <div className="flex items-center gap-1">
                Income Level *
                <Tooltip
                  content={
                    <div className="text-sm max-w-xs">
                      <p>Scale 1–8:</p>
                      <p>1 = Less than $10,000</p>
                      <p>2 = $10,000–$15,000</p>
                      <p>3 = $15,000–$20,000</p>
                      <p>4 = $20,000–$25,000</p>
                      <p>5 = $25,000-$35,000</p>
                      <p>6 = $35,000–$50,000</p>
                      <p>7 = $50,000–$75,000</p>
                      <p>8 = $75,000 or more</p>
                    </div>
                  }
                  showArrow
                  placement="right"
                >
                  <span className="text-primary cursor-pointer text-sm">ⓘ</span>
                </Tooltip>
              </div>
            }
            name="Age"
            errorMessage="This field is required"
            type="number"
            labelPlacement="outside"
            placeholder="Enter your Age"
            classNames={{
              label: "!text-default-500",
            }}
          />
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
