import { title } from "@/components/primitives";

export default function AboutPage() {
  return (
    <div className="p-6">
      <h1 className="text-center justify-self-center mb-10 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent text-6xl font-bold drop-shadow-[0_0_10px_rgba(255,255,255,0.3)] animate-pulse hover:scale-105 transition-all duration-300 ease-in-out cursor-pointer">
        About
      </h1>
      <p className="mt-4 text-lg">
        Welcome to the Diabetes Prediction Application! This project is designed
        to help users predict the likelihood of diabetes based on various health
        metrics. Our goal is to provide an easy-to-use tool that empowers
        individuals to take proactive steps in managing their health.
      </p>
      <p className="mt-4 text-lg">
        This application leverages machine learning models to analyze
        user-provided data and generate predictions. It is built using modern
        web technologies, including Next.js, Tailwind CSS, and Hero UI
        components, ensuring a seamless and responsive user experience.
      </p>
      <p className="mt-4 text-lg">
        Please note that this tool is for informational purposes only and should
        not replace professional medical advice. Always consult with a
        healthcare provider for any medical concerns.
      </p>
    </div>
  );
}
