/**
 * CreateTripPage - Landing page for creating a new trip
 * Uses react-hook-form + zod for validation
 * Navigates to trip dashboard on successful creation
 */
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useCreateTrip } from '../api/hooks';
import type { TripCreate } from '../types/db';

// Zod validation schema
const tripFormSchema = z.object({
  name: z.string().min(3, 'Trip name must be at least 3 characters').max(100, 'Trip name too long'),
  start_date: z.string().optional().nullable(),
  end_date: z.string().optional().nullable(),
});

type TripFormData = z.infer<typeof tripFormSchema>;

export const CreateTripPage = () => {
  const navigate = useNavigate();
  const createTripMutation = useCreateTrip();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TripFormData>({
    resolver: zodResolver(tripFormSchema),
    defaultValues: {
      name: '',
      start_date: null,
      end_date: null,
    },
  });

  const onSubmit = async (data: TripFormData) => {
    try {
      const tripData: TripCreate = {
        name: data.name,
        start_date: data.start_date || null,
        end_date: data.end_date || null,
        participants: [],
      };

      const createdTrip = await createTripMutation.mutateAsync(tripData);
      toast.success(`Trip "${createdTrip.name}" created successfully!`);
      navigate(`/trip/${createdTrip.id}`);
    } catch (error) {
      toast.error('Failed to create trip. Please try again.');
      console.error('Create trip error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-500 to-indigo-600 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="bg-white rounded-3xl shadow-2xl p-8 md:p-12 max-w-md w-full"
      >
        <motion.h1
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500 mb-2 text-center"
        >
          PackVote 2.0
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-gray-600 text-center mb-8"
        >
          Plan your perfect group trip together
        </motion.p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <label htmlFor="name" className="block text-sm font-semibold text-gray-700 mb-2">
              Trip Name *
            </label>
            <Input
              id="name"
              type="text"
              placeholder="e.g., Summer Europe Adventure"
              {...register('name')}
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
            )}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            <label htmlFor="start_date" className="block text-sm font-semibold text-gray-700 mb-2">
              Start Date (Optional)
            </label>
            <Input
              id="start_date"
              type="date"
              {...register('start_date')}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
          >
            <label htmlFor="end_date" className="block text-sm font-semibold text-gray-700 mb-2">
              End Date (Optional)
            </label>
            <Input
              id="end_date"
              type="date"
              {...register('end_date')}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Button
              type="submit"
              isLoading={createTripMutation.isPending}
              className="w-full bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 text-white shadow-lg"
            >
              {createTripMutation.isPending ? 'Creating...' : 'Create Trip'}
            </Button>
          </motion.div>
        </form>
      </motion.div>
    </div>
  );
};
