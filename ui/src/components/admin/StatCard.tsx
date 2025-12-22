import React from 'react';
import { motion } from 'framer-motion';
import { ArrowUp, ArrowDown, BoxIcon } from 'lucide-react';
interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: BoxIcon;
  color?: 'sage' | 'orange' | 'red' | 'blue';
}
export function StatCard({
  title,
  value,
  change,
  icon: Icon,
  color = 'sage'
}: StatCardProps) {
  const colorClasses = {
    sage: 'bg-sage/10 text-sage',
    orange: 'bg-orange-100 text-orange-600',
    red: 'bg-red-100 text-red-600',
    blue: 'bg-blue-100 text-blue-600'
  };
  return <motion.div initial={{
    opacity: 0,
    y: 10
  }} animate={{
    opacity: 1,
    y: 0
  }} className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-xl ${colorClasses[color]}`}>
          <Icon size={20} />
        </div>
        {change !== undefined && <div className={`flex items-center text-xs font-medium ${change >= 0 ? 'text-sage' : 'text-red-500'}`}>
            {change >= 0 ? <ArrowUp size={14} className="mr-1" /> : <ArrowDown size={14} className="mr-1" />}
            {Math.abs(change)}%
          </div>}
      </div>
      <h3 className="text-secondary text-sm font-medium mb-1">{title}</h3>
      <p className="text-2xl font-light text-primary">{value}</p>
    </motion.div>;
}