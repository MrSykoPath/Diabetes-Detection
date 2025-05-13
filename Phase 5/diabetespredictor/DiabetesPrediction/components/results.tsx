"use client";
import React from "react";
import { Card, CardHeader, CardBody } from "@heroui/card";
import { Progress } from "@heroui/progress";

export default function Results({
  positive,
  probability,
}: {
  positive: boolean;
  probability: number | undefined;
}) {
  return (
    <div className="mt-10 w-6/12 mx-auto">
      <Card
        className={
          "py-4 border-l-8 " +
          (positive
            ? "border-red-500 bg-red-50 dark:bg-red-900/20"
            : "border-green-500 bg-green-50 dark:bg-green-900/20")
        }
      >
        <CardHeader className="pb-4 pt-2 px-4 flex-col items-center">
          <p className="text-xl uppercase font-bold">Results</p>
        </CardHeader>
        <CardBody className="overflow-visible py-2 grid grid-cols-4 gap-4 items-center justify-center">
          <svg
            fill={positive ? "#dc2626" : "#16a34a"}
            width="default"
            height="default"
            viewBox="0 0 32 32"
            xmlns="http://www.w3.org/2000/svg"
            className="col-span-4 md:col-span-1 size-14 sm:size-16 md:size-24 lg:size-28 mx-auto mb-2"
          >
            <title />

            <g data-name="Layer 17" id="Layer_17">
              <path d="M25,6H22a4.09,4.09,0,0,0-4.08-4H14.09A4.09,4.09,0,0,0,10,6H7A1,1,0,0,0,6,7V29a1,1,0,0,0,1,1H25a1,1,0,0,0,1-1V7A1,1,0,0,0,25,6ZM14.09,4h3.82A2.1,2.1,0,0,1,20,6H12A2.1,2.1,0,0,1,14.09,4ZM24,28H8V8H24Z" />

              <path d="M14,13h1v1a1,1,0,0,0,2,0V13h1a1,1,0,0,0,0-2H17V10a1,1,0,0,0-2,0v1H14a1,1,0,0,0,0,2Z" />

              <path d="M22,24H10a1,1,0,0,0,0,2H22a1,1,0,0,0,0-2Z" />

              <path d="M22,21H10a1,1,0,0,0,0,2H22a1,1,0,0,0,0-2Z" />

              <path d="M9,19a1,1,0,0,0,1,1H22a1,1,0,0,0,0-2H10A1,1,0,0,0,9,19Z" />
            </g>
          </svg>
          <Progress
            classNames={{
              base: "md:col-span-3 col-span-4",
              track: "drop-shadow-md border border-default",
              indicator: positive
                ? "bg-gradient-to-r from-green-500 via-yellow-500 to-red-500"
                : "bg-gradient-to-r from-red-500 via-yellow-500 to-green-500",
              label: "tracking-wider font-medium text-default-600",
              value: "text-foreground/60",
            }}
            label="Confidence"
            radius="sm"
            showValueLabel={true}
            size="sm"
            value={2 * Math.abs(probability! - 0.5) * 100}
          />
          <p
            className={
              "col-span-4 text-center text-lg font-semibold " +
              (positive ? "text-red-500" : "text-green-500")
            }
          >
            {positive
              ? "You are at risk of diabetes."
              : "You are not at risk of diabetes."}
          </p>
        </CardBody>
      </Card>
    </div>
  );
}
