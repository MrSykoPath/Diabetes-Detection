import React from "react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
} from "@heroui/modal";
import { Button, PressEvent } from "@heroui/button";
import { Radio, RadioGroup } from "@heroui/radio";
import { addToast } from "@heroui/toast";
import { cn } from "@heroui/theme";
import axios from "axios";
export default function Truth({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const [truth, settruth] = React.useState<number>(0);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const handleTruthDropdownChange = React.useCallback((value: string) => {
    settruth(parseInt(value));
    console.log(parseInt(value));
  }, []);

  const onSubmit = async (e: PressEvent) => {
    setLoading(true);
    const data = { Diabetes_binary: truth };
    console.log(data);
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/add_feedback",
        data,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      console.log(response.data);
      onClose();
      setError(null);
    } catch (error: any) {
      console.error("There was an error!", error);
      setError("There was an error!");
      throw error; // Re-throw the error to be caught in the onPress handler
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal backdrop="blur" isOpen={isOpen} onClose={onClose} className="p-8">
      <ModalContent>
        {(modalOnClose) => (
          <>
            <ModalHeader className="flex flex-col gap-1">
              <h2 className="text-3xl text-center font-medium bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                Submit Your Diagnosis
              </h2>
            </ModalHeader>
            <ModalBody>
              <p>
                In order to make our model better, could you enter your actual
                diagnosis? It will help us improve our model and make it more
                accurate for future patients.
              </p>

              {/* Use Hero UI's RadioGroup component */}
              <RadioGroup
                label="Select your diagnosis:"
                value={String(truth)}
                onValueChange={(value) => handleTruthDropdownChange(value)}
                orientation="vertical"
                className="gap-2"
                color="secondary"
              >
                <Radio value="0">Non-Diabetic</Radio>
                <Radio value="1">Prediabetic or Diabetic</Radio>
              </RadioGroup>
            </ModalBody>
            <ModalFooter>
              <Button
                color="secondary"
                variant="solid"
                className="w-full"
                onPress={async (e) => {
                  onSubmit(e)
                    .then(() => {
                      addToast({
                        title: "Success",
                        description: "Your feedback has been submitted.",
                        classNames: {
                          base: cn([
                            "bg-default-50 dark:bg-transparent shadow-sm",
                            "border border-l-8 rounded-md rounded-l-none",
                            "flex flex-col items-start",
                            "text-gray-900 dark:text-gray-100",
                            "border-success-200 dark:border-success-100 border-l-success",
                          ]),
                          icon: "w-6 h-6 fill-current",
                        },
                        color: "foreground",
                      });
                    })
                    .catch((error) => {
                      addToast({
                        title: "Error",
                        description: error.message,
                        classNames: {
                          base: cn([
                            "bg-default-50 dark:bg-transparent shadow-sm",
                            "border border-l-8 rounded-md rounded-l-none",
                            "flex flex-col items-start",
                            "text-gray-900 dark:text-gray-100",
                            "border-danger-200 dark:border-danger-100 border-l-danger",
                          ]),
                          icon: "w-6 h-6 fill-current",
                        },
                        color: "foreground",
                      });
                    });
                }}
                isLoading={loading}
              >
                Submit
              </Button>
            </ModalFooter>
          </>
        )}
      </ModalContent>
    </Modal>
  );
}
