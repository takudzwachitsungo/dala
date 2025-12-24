import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
export interface Entry {
  id: string;
  text: string;
  mood: number;
  timestamp: Date;
}
interface EntryListProps {
  entries: Entry[];
}
export function EntryList({
  entries
}: EntryListProps) {
  if (entries.length === 0) {
    return <motion.div initial={{
      opacity: 0
    }} animate={{
      opacity: 1
    }} transition={{
      duration: 1,
      delay: 0.5
    }} className="text-center text-subtle mt-24 font-light italic">
        Breathe in. Start writing.
      </motion.div>;
  }
  return <div className="w-full max-w-2xl mx-auto space-y-12">
      <AnimatePresence mode="popLayout">
        {entries.map(entry => <motion.div key={entry.id} layout initial={{
        opacity: 0,
        y: 20
      }} animate={{
        opacity: 1,
        y: 0
      }} exit={{
        opacity: 0,
        scale: 0.95
      }} transition={{
        duration: 0.8,
        ease: [0.16, 1, 0.3, 1]
      }} className="group">
            <div className="flex flex-col space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 rounded-full bg-sage opacity-80" aria-hidden="true" />
                <span className="text-xs text-secondary tracking-wider uppercase">
                  {new Intl.DateTimeFormat('en-US', {
                month: 'long',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric'
              }).format(entry.timestamp)}
                </span>
              </div>

              <p className="text-primary leading-relaxed whitespace-pre-wrap pl-5 border-l-2 border-sage/20 transition-colors duration-500">
                {entry.text}
              </p>
            </div>

            <div className="h-px w-full bg-divider mt-12 opacity-40" />
          </motion.div>)}
      </AnimatePresence>
    </div>;
}