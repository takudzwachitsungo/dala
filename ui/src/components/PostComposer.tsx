import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send } from 'lucide-react';
interface PostComposerProps {
  onSubmit: (content: string) => void;
  placeholder?: string;
}
export function PostComposer({
  onSubmit,
  placeholder = 'Share your thoughts...'
}: PostComposerProps) {
  const [content, setContent] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const maxLength = 500;
  const handleSubmit = () => {
    if (!content.trim()) return;
    onSubmit(content);
    setContent('');
    setIsFocused(false);
  };
  return <div className="bg-white rounded-2xl p-4 shadow-sm border border-divider/50">
      <div className="relative">
        <textarea value={content} onChange={e => setContent(e.target.value)} onFocus={() => setIsFocused(true)} onBlur={() => !content && setIsFocused(false)} placeholder={placeholder} maxLength={maxLength} className="w-full bg-transparent text-sm text-primary placeholder-secondary/50 resize-none focus:outline-none min-h-[80px]" />

        <AnimatePresence>
          {(isFocused || content) && <motion.div initial={{
          opacity: 0,
          height: 0
        }} animate={{
          opacity: 1,
          height: 'auto'
        }} exit={{
          opacity: 0,
          height: 0
        }} className="flex items-center justify-between mt-2 pt-2 border-t border-divider/30">
              <span className={`text-[10px] ${content.length > maxLength * 0.9 ? 'text-orange-500' : 'text-secondary'}`}>
                {content.length}/{maxLength}
              </span>

              <button onClick={handleSubmit} disabled={!content.trim()} className="bg-sage text-white rounded-full p-2 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-sage-hover transition-colors">
                <Send size={14} />
              </button>
            </motion.div>}
        </AnimatePresence>
      </div>
    </div>;
}