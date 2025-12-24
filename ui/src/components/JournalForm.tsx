import React, { useState, useRef, useImperativeHandle, forwardRef } from 'react';
import { motion } from 'framer-motion';
interface JournalFormProps {
  onSubmit: (text: string) => void;
  isSubmitting?: boolean;
}
export const JournalForm = forwardRef<{ focus: () => void }, JournalFormProps>((
  { onSubmit, isSubmitting = false },
  ref
) => {
  const [text, setText] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useImperativeHandle(ref, () => ({
    focus: () => {
      textareaRef.current?.focus();
      textareaRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }));

  const handleSubmit = () => {
    if (!text.trim()) return;
    onSubmit(text);
    setText('');
  };
  return <div className="w-full max-w-2xl mx-auto mt-12 mb-20">
      <div className="relative">
        <motion.textarea
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="How are you feeling right now?"
          className="w-full bg-transparent text-primary text-lg leading-relaxed placeholder-subtle resize-none focus:outline-none py-6 px-4 min-h-[160px]"
          style={{
            borderBottom: isFocused ? '1px solid #A3B18A' : '0px solid transparent'
          }}
          transition={{
            duration: 0.5
          }} />

        {/* Subtle underline when not focused to show area exists, optional based on "no border at rest" */}
        {!isFocused && text.length === 0 && <div className="absolute bottom-0 left-0 right-0 h-px bg-transparent" />}
      </div>

      <div className="flex justify-end mt-8">
        <motion.button onClick={handleSubmit} disabled={!text.trim() || isSubmitting} initial={{
        opacity: 0,
        y: 10
      }} animate={{
        opacity: text.trim() ? 1 : 0,
        y: text.trim() ? 0 : 10,
        pointerEvents: text.trim() ? 'auto' : 'none'
      }} whileHover={{
        scale: 1.02
      }} whileTap={{
        scale: 0.98
      }} className="bg-sage hover:bg-sage-hover text-white text-sm font-medium py-3 px-8 rounded-full transition-colors duration-300 shadow-sm">
          {isSubmitting ? 'Saving...' : 'Save Entry'}
        </motion.button>
      </div>
    </div>;
});