import React from 'react';
import { motion } from 'framer-motion';
interface MoodSelectorProps {
  selectedMood: number;
  onSelectMood: (mood: number) => void;
}
const moods = [{
  value: 1,
  label: 'Rough'
}, {
  value: 2,
  label: 'Down'
}, {
  value: 3,
  label: 'Okay'
}, {
  value: 4,
  label: 'Good'
}, {
  value: 5,
  label: 'Great'
}];
export function MoodSelector({
  selectedMood,
  onSelectMood
}: MoodSelectorProps) {
  return <div className="flex flex-col items-center space-y-8 py-8">
      <div className="flex items-center justify-center space-x-12">
        {moods.map(mood => {
        const isSelected = selectedMood === mood.value;
        return <button key={mood.value} onClick={() => onSelectMood(mood.value)} className="group flex flex-col items-center focus:outline-none" aria-label={`Select mood: ${mood.label}`}>
              <div className="relative flex items-center justify-center h-8 w-8">
                <motion.div initial={false} animate={{
              scale: isSelected ? 1.2 : 1,
              backgroundColor: isSelected ? '#A3B18A' : 'transparent',
              borderColor: isSelected ? '#A3B18A' : '#A8A29E',
              borderWidth: isSelected ? 0 : 1.5
            }} transition={{
              duration: 0.4,
              ease: 'easeOut'
            }} className="rounded-full w-3 h-3 box-border" style={{
              width: isSelected ? 16 : 12,
              height: isSelected ? 16 : 12
            }} />

                {/* Hover effect ring */}
                <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-10 transition-opacity duration-300 bg-sage scale-150" />
              </div>

              <motion.span animate={{
            opacity: isSelected ? 1 : 0.5,
            y: isSelected ? 4 : 0,
            color: isSelected ? '#78716C' : '#D6D3D1'
          }} className="text-xs mt-2 font-medium tracking-wide">
                {mood.label}
              </motion.span>
            </button>;
      })}
      </div>
    </div>;
}