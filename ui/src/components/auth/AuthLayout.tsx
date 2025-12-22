import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
interface AuthLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  onBack?: () => void;
}
export function AuthLayout({
  children,
  title,
  subtitle,
  onBack
}: AuthLayoutProps) {
  return <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6">
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} className="w-full max-w-md">
        {onBack && <button onClick={onBack} className="mb-8 p-2 -ml-2 text-secondary hover:text-primary transition-colors rounded-full hover:bg-secondary/10 inline-flex">
            <ArrowLeft size={24} />
          </button>}

        <div className="text-center mb-10">
          <h1 className="text-4xl font-light text-primary tracking-tight mb-2">
            Dala
          </h1>
          {title && <h2 className="text-xl font-medium text-primary mt-6">{title}</h2>}
          {subtitle && <p className="text-secondary text-sm mt-2">{subtitle}</p>}
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-sm border border-divider/50">
          {children}
        </div>

        <p className="text-center text-xs text-subtle mt-8">
          Private. Non-judgmental. At your pace.
        </p>
      </motion.div>
    </div>;
}