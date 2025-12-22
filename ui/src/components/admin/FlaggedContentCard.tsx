import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, XCircle, MessageSquare } from 'lucide-react';
interface FlaggedContentCardProps {
  id: number;
  content: string;
  author: string;
  reason: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
  onAction: (id: number, action: 'approve' | 'dismiss' | 'escalate') => void;
}
export function FlaggedContentCard({
  id,
  content,
  author,
  reason,
  severity,
  timestamp,
  onAction
}: FlaggedContentCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const severityColors = {
    low: 'bg-yellow-100 text-yellow-700',
    medium: 'bg-orange-100 text-orange-700',
    high: 'bg-red-100 text-red-700'
  };
  return <motion.div layout className="bg-white rounded-xl border border-divider/50 overflow-hidden">
      <div className="p-4 flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide ${severityColors[severity]}`}>
              {severity} Risk
            </span>
            <span className="text-xs text-secondary">• {timestamp}</span>
            <span className="text-xs text-secondary">• by {author}</span>
          </div>

          <h4 className="text-sm font-medium text-red-600 flex items-center mb-2">
            <AlertTriangle size={14} className="mr-1" />
            Flagged for: {reason}
          </h4>

          <p className={`text-sm text-primary leading-relaxed ${!isExpanded && 'line-clamp-2'}`}>
            "{content}"
          </p>

          {content.length > 100 && <button onClick={() => setIsExpanded(!isExpanded)} className="text-xs text-sage font-medium mt-1 hover:underline">
              {isExpanded ? 'Show less' : 'Show full context'}
            </button>}
        </div>

        <div className="flex flex-col space-y-2">
          <button onClick={() => onAction(id, 'dismiss')} className="p-2 text-secondary hover:text-primary hover:bg-background rounded-lg transition-colors" title="Dismiss Flag">
            <XCircle size={20} />
          </button>
          <button onClick={() => onAction(id, 'approve')} className="p-2 text-sage hover:text-sage-hover hover:bg-sage/10 rounded-lg transition-colors" title="Approve Content">
            <CheckCircle size={20} />
          </button>
          <button onClick={() => onAction(id, 'escalate')} className="p-2 text-red-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Escalate Case">
            <MessageSquare size={20} />
          </button>
        </div>
      </div>
    </motion.div>;
}