import React from "react";
import { Card, CardHeader, CardBody } from "@heroui/card";
import { Image } from "@heroui/image";
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
          <Image
            alt="Card background"
            className="object-cover rounded-xl"
            src="https://heroui.com/images/hero-card-complete.jpeg"
            width={270}
          />
          <Progress
            classNames={{
              base: "col-span-3",
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
            value={probability ? probability * 100 : 0}
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
