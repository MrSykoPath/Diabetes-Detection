import { Link } from "@heroui/link";
import { Snippet } from "@heroui/snippet";
import { Code } from "@heroui/code";
import { button as buttonStyles } from "@heroui/theme";

import { siteConfig } from "@/config/site";
import { title, subtitle } from "@/components/primitives";
import { GithubIcon } from "@/components/icons";

export default function Home() {
  return (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
      <div className="inline-block max-w-xl text-center justify-center">
        <span className={title()}>Detect&nbsp;</span>
        <span className={title({ color: "violet" })}>Diabetes&nbsp;</span>
        <br />
        <span className={title()}>
          with a click of a button and{" "}
          <span className={title({ color: "cyan" })}> Machine Learning </span>
        </span>
        <div className={subtitle({ class: "mt-4" })}>
          ⚠️ Disclaimer: “This tool is for informational purposes only. Always
          consult a medical professional.”
        </div>
      </div>

      <div className="flex gap-3">
        <Link
          className={buttonStyles({
            color: "secondary",
            radius: "full",
            variant: "shadow",
          })}
          href="/predictor"
        >
          Start
        </Link>
        <Link
          isExternal
          className={buttonStyles({ variant: "bordered", radius: "full" })}
          href="https://github.com/MrSykoPath/Diabetes-Detection"
        >
          <GithubIcon size={20} />
          GitHub
        </Link>
      </div>

      <div className="mt-8">
        <Snippet hideCopyButton hideSymbol variant="flat">
          <span className="text-4xl bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            75% Accuracy!
          </span>
        </Snippet>
      </div>
    </section>
  );
}
