/**
 * ImportFromUrlModal - Import activities from social media URLs
 * Allows users to paste URLs from TikTok, Instagram, etc. to extract activity suggestions
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { useImportFromUrl, useAddActivityToDay } from '../api/hooks';
import { Button } from './ui/button';
import { Input } from './ui/input';
import type { ImportedActivitySuggestion, ImportFromUrlRequest } from '../types/db';

const importSchema = z.object({
  url: z.string().url('Please enter a valid URL'),
});

interface ImportFromUrlModalProps {
  tripId: string;
  onClose: () => void;
}

export const ImportFromUrlModal = ({ tripId, onClose }: ImportFromUrlModalProps) => {
  const [importedActivities, setImportedActivities] = useState<ImportedActivitySuggestion[]>([]);
  const [selectedDayId, setSelectedDayId] = useState<string>('');
  const [selectedActivities, setSelectedActivities] = useState<Set<number>>(new Set());

  const importMutation = useImportFromUrl();
  const addActivityMutation = useAddActivityToDay();

  const { register, handleSubmit, formState: { errors } } = useForm<{ url: string }>({
    resolver: zodResolver(importSchema),
  });

  const onImport = async (data: { url: string }) => {
    try {
      const request: ImportFromUrlRequest = { url: data.url };
      const result = await importMutation.mutateAsync({ tripId, request });
      
      if (result.suggested_activities.length === 0) {
        toast.error('No activities found at this URL. Try a different link.');
        return;
      }

      setImportedActivities(result.suggested_activities);
      toast.success(`Found ${result.suggested_activities.length} activity suggestions!`);
    } catch (error) {
      toast.error('Failed to import from URL. Please try again.');
    }
  };

  const toggleActivity = (index: number) => {
    const newSelected = new Set(selectedActivities);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedActivities(newSelected);
  };

  const handleAddToItinerary = async () => {
    if (!selectedDayId) {
      toast.error('Please select a day to add activities to');
      return;
    }

    if (selectedActivities.size === 0) {
      toast.error('Please select at least one activity');
      return;
    }

    try {
      const promises = Array.from(selectedActivities).map(index => {
        const activity = importedActivities[index];
        return addActivityMutation.mutateAsync({
          dayId: selectedDayId,
          activity: {
            title: activity.title,
            notes: activity.notes || null,
            location: activity.location || null,
            start_time: null,
            end_time: null,
          },
          tripId,
        });
      });

      await Promise.all(promises);
      toast.success(`Added ${selectedActivities.size} activities to itinerary!`);
      onClose();
    } catch (error) {
      toast.error('Failed to add activities. Please try again.');
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800';
    if (confidence >= 0.5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-orange-100 text-orange-800';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-3xl shadow-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              🌐 Import from Social Media
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Paste a link from TikTok, Instagram, YouTube, or Pinterest
            </p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl font-bold">
            ×
          </button>
        </div>

        {/* URL Input Form */}
        {importedActivities.length === 0 && (
          <form onSubmit={handleSubmit(onImport)} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">URL</label>
              <Input
                {...register('url')}
                placeholder="https://www.tiktok.com/@user/video/..."
                className="w-full"
              />
              {errors.url && (
                <p className="mt-1 text-sm text-red-600">{errors.url.message}</p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
              disabled={importMutation.isPending}
            >
              {importMutation.isPending ? 'Importing...' : 'Import Activities'}
            </Button>

            <div className="bg-blue-50 border-l-4 border-blue-500 p-3 rounded">
              <p className="text-xs text-blue-800">
                <strong>How it works:</strong> Our AI will analyze the content and extract potential travel activities, 
                locations, and recommendations for your trip.
              </p>
            </div>
          </form>
        )}

        {/* Imported Activities Display */}
        {importedActivities.length > 0 && (
          <div className="space-y-4">
            <div className="bg-green-50 border-l-4 border-green-500 p-3 rounded mb-4">
              <p className="text-sm text-green-800">
                ✨ Found {importedActivities.length} activity suggestions! Select the ones you want to add.
              </p>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto mb-4">
              {importedActivities.map((activity, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`border-2 rounded-xl p-4 cursor-pointer transition-all ${
                    selectedActivities.has(index)
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                  onClick={() => toggleActivity(index)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-bold text-gray-800 flex-1">{activity.title}</h4>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getConfidenceColor(activity.confidence)}`}>
                        {(activity.confidence * 100).toFixed(0)}% match
                      </span>
                      <input
                        type="checkbox"
                        checked={selectedActivities.has(index)}
                        onChange={() => toggleActivity(index)}
                        className="w-5 h-5"
                      />
                    </div>
                  </div>
                  {activity.notes && (
                    <p className="text-sm text-gray-600 mb-2">{activity.notes}</p>
                  )}
                  <div className="flex flex-wrap gap-2 text-xs">
                    {activity.location && (
                      <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        📍 {activity.location}
                      </span>
                    )}
                    {activity.estimated_duration && (
                      <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        ⏱️ {activity.estimated_duration}
                      </span>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Day Selection - Simplified for V1 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Add to Itinerary (Optional - implement day selector)
              </label>
              <p className="text-xs text-gray-500 mb-4">
                Note: Day selection requires fetching trip itinerary days. For now, activities are extracted 
                and you can manually add them to specific days.
              </p>
            </div>

            <div className="flex gap-3">
              <Button
                onClick={() => {
                  setImportedActivities([]);
                  setSelectedActivities(new Set());
                }}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800"
              >
                Import Another
              </Button>
              <Button
                onClick={onClose}
                className="flex-1 bg-purple-600 hover:bg-purple-700 text-white"
              >
                Done
              </Button>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
};
