import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Plus, Trash2, Save } from 'lucide-react';
import { apiClient } from '../api/client';

interface SafetyPlanModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface SafetyPlan {
  warning_signs: string[];
  internal_coping: string[];
  social_contacts: string[];
  people_to_ask: string[];
  professionals: string[];
  emergency_contacts: string[];
  safe_environment: string;
  reasons_to_live: string[];
}

export function SafetyPlanModal({ isOpen, onClose }: SafetyPlanModalProps) {
  const [plan, setPlan] = useState<SafetyPlan>({
    warning_signs: [],
    internal_coping: [],
    social_contacts: [],
    people_to_ask: [],
    professionals: [],
    emergency_contacts: [],
    safe_environment: '',
    reasons_to_live: []
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadPlan();
    }
  }, [isOpen]);

  const loadPlan = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getSafetyPlan();
      // Ensure safe_environment is a string, not null
      setPlan({
        ...data,
        safe_environment: data.safe_environment || ''
      });
    } catch (error) {
      console.error('Failed to load safety plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const savePlan = async () => {
    try {
      setSaving(true);
      await apiClient.updateSafetyPlan(plan);
      onClose();
    } catch (error) {
      console.error('Failed to save safety plan:', error);
      alert('Failed to save safety plan. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const addItem = (field: keyof SafetyPlan) => {
    const value = window.prompt(`Add new item:`);
    if (value && value.trim()) {
      setPlan(prev => ({
        ...prev,
        [field]: [...(prev[field] as string[]), value.trim()]
      }));
    }
  };

  const removeItem = (field: keyof SafetyPlan, index: number) => {
    setPlan(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).filter((_, i) => i !== index)
    }));
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-divider/50 px-6 py-4 flex items-center justify-between rounded-t-3xl">
            <h2 className="text-xl font-medium text-primary">My Safety Plan</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-background rounded-full transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto"></div>
              <p className="text-secondary text-sm mt-4">Loading your safety plan...</p>
            </div>
          ) : (
            <div className="p-6 space-y-8">
              {/* Warning Signs */}
              <Section
                title="Warning Signs"
                description="How do I know when I'm starting to feel unsafe?"
                items={plan.warning_signs}
                onAdd={() => addItem('warning_signs')}
                onRemove={(i) => removeItem('warning_signs', i)}
              />

              {/* Internal Coping */}
              <Section
                title="Things I Can Do On My Own"
                description="Activities or coping strategies that help me feel better"
                items={plan.internal_coping}
                onAdd={() => addItem('internal_coping')}
                onRemove={(i) => removeItem('internal_coping', i)}
              />

              {/* Social Contacts */}
              <Section
                title="People Who Can Distract Me"
                description="Friends or family I can spend time with"
                items={plan.social_contacts}
                onAdd={() => addItem('social_contacts')}
                onRemove={(i) => removeItem('social_contacts', i)}
              />

              {/* People to Ask */}
              <Section
                title="People I Can Ask for Help"
                description="Trusted individuals I can talk to about how I'm feeling"
                items={plan.people_to_ask}
                onAdd={() => addItem('people_to_ask')}
                onRemove={(i) => removeItem('people_to_ask', i)}
              />

              {/* Professionals */}
              <Section
                title="Professional Contacts"
                description="Therapists, counselors, or crisis services"
                items={plan.professionals}
                onAdd={() => addItem('professionals')}
                onRemove={(i) => removeItem('professionals', i)}
              />

              {/* Emergency Contacts */}
              <Section
                title="Emergency Contacts"
                description="Crisis hotlines and emergency services"
                items={plan.emergency_contacts}
                onAdd={() => addItem('emergency_contacts')}
                onRemove={(i) => removeItem('emergency_contacts', i)}
                defaultItems={['988 - Suicide & Crisis Lifeline', '911 - Emergency Services']}
              />

              {/* Safe Environment */}
              <div>
                <h3 className="text-sm font-medium text-primary mb-1">Making My Environment Safe</h3>
                <p className="text-xs text-secondary mb-3">Steps I can take to make my space safer</p>
                <textarea
                  value={plan.safe_environment}
                  onChange={(e) => setPlan(prev => ({ ...prev, safe_environment: e.target.value }))}
                  placeholder="e.g., Remove harmful items, ask someone to keep certain things for me..."
                  className="w-full bg-background border border-divider rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all resize-none"
                  rows={3}
                />
              </div>

              {/* Reasons to Live */}
              <Section
                title="Reasons for Living"
                description="What makes life worth living for me"
                items={plan.reasons_to_live}
                onAdd={() => addItem('reasons_to_live')}
                onRemove={(i) => removeItem('reasons_to_live', i)}
              />
            </div>
          )}

          {/* Footer */}
          <div className="sticky bottom-0 bg-white border-t border-divider/50 px-6 py-4 rounded-b-3xl">
            <button
              onClick={savePlan}
              disabled={saving}
              className="w-full bg-sage text-white py-3 rounded-xl font-medium hover:bg-sage/90 transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save size={18} />
                  <span>Save Safety Plan</span>
                </>
              )}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

interface SectionProps {
  title: string;
  description: string;
  items: string[];
  onAdd: () => void;
  onRemove: (index: number) => void;
  defaultItems?: string[];
}

function Section({ title, description, items, onAdd, onRemove, defaultItems = [] }: SectionProps) {
  const allItems = [...defaultItems, ...items];
  
  return (
    <div>
      <h3 className="text-sm font-medium text-primary mb-1">{title}</h3>
      <p className="text-xs text-secondary mb-3">{description}</p>
      
      <div className="space-y-2">
        {allItems.map((item, index) => (
          <div
            key={index}
            className="flex items-center space-x-2 bg-background rounded-lg px-4 py-2.5 group"
          >
            <span className="flex-1 text-sm text-primary">{item}</span>
            {index >= defaultItems.length && (
              <button
                onClick={() => onRemove(index - defaultItems.length)}
                className="p-1 opacity-0 group-hover:opacity-100 hover:text-red-500 transition-all"
              >
                <Trash2 size={14} />
              </button>
            )}
          </div>
        ))}
        
        <button
          onClick={onAdd}
          className="w-full border-2 border-dashed border-divider rounded-lg px-4 py-2.5 text-sm text-secondary hover:text-sage hover:border-sage transition-colors flex items-center justify-center space-x-2"
        >
          <Plus size={16} />
          <span>Add Item</span>
        </button>
      </div>
    </div>
  );
}
