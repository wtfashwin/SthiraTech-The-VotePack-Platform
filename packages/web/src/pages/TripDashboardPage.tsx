/**
 * TripDashboardPage - Main dashboard for managing a trip
 * Displays all trip information, participants, itinerary, polls, and expenses
 */
import { useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { useTrip, useAddParticipant, useCreateItineraryDay, useAddActivityToDay, useCreatePoll, useCastVote, useCreateExpense, useTripBalance } from '../api/hooks';
import { useUiStore } from '../store/uiStore';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import type { ParticipantCreate, ItineraryDayCreate, ActivityCreate, PollCreate, VoteCreate, ExpenseCreate, ExpenseSplitBase } from '../types/db';

// --- Form Schemas ---
const participantSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
});

const daySchema = z.object({
  date: z.string().min(1, 'Date is required'),
  title: z.string().optional(),
});

const activitySchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters'),
  notes: z.string().optional(),
  start_time: z.string().optional(),
  end_time: z.string().optional(),
  location: z.string().optional(),
});

type ActivityFormData = z.infer<typeof activitySchema>;

const pollSchema = z.object({
  question: z.string().min(5, 'Question must be at least 5 characters'),
  option1: z.string().min(1, 'Option 1 is required'),
  option2: z.string().min(1, 'Option 2 is required'),
  option3: z.string().optional(),
  option4: z.string().optional(),
});

const expenseSchema = z.object({
  description: z.string().min(3, 'Description required'),
  amount: z.number().positive('Amount must be positive'),
  currency: z.string(),
  date: z.string().min(1, 'Date is required'),
  paid_by_id: z.string().min(1, 'Payer is required'),
});

type ExpenseFormData = z.infer<typeof expenseSchema>;

export const TripDashboardPage = () => {
  const { tripId } = useParams<{ tripId: string }>();
  const { data: trip, isLoading, error } = useTrip(tripId!);
  const { data: balances } = useTripBalance(tripId!);

  const {
    isAddParticipantModalOpen,
    setAddParticipantModalOpen,
    isAddDayModalOpen,
    setAddDayModalOpen,
    isAddActivityModalOpen,
    setAddActivityModalOpen,
    isCreatePollModalOpen,
    setCreatePollModalOpen,
    isAddExpenseModalOpen,
    setAddExpenseModalOpen,
    selectedDayId,
    setSelectedDayId,
  } = useUiStore();

  const addParticipantMutation = useAddParticipant();
  const createDayMutation = useCreateItineraryDay();
  const addActivityMutation = useAddActivityToDay();
  const createPollMutation = useCreatePoll();
  const castVoteMutation = useCastVote();
  const createExpenseMutation = useCreateExpense();

  // Form hooks
  const participantForm = useForm<ParticipantCreate>({ resolver: zodResolver(participantSchema) });
  const dayForm = useForm<z.infer<typeof daySchema>>({ resolver: zodResolver(daySchema) });
  const activityForm = useForm<ActivityFormData>({ resolver: zodResolver(activitySchema) });
  const pollForm = useForm<z.infer<typeof pollSchema>>({ resolver: zodResolver(pollSchema) });
  const expenseForm = useForm<ExpenseFormData>({ 
    resolver: zodResolver(expenseSchema),
    defaultValues: { currency: 'USD' }
  });

  // Loading and error states
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-500 to-indigo-600 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-white text-2xl font-bold"
        >
          Loading trip...
        </motion.div>
      </div>
    );
  }

  if (error || !trip) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-500 to-indigo-600 flex items-center justify-center">
        <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
          <p className="text-gray-700">Trip not found or failed to load.</p>
        </div>
      </div>
    );
  }

  // --- Event Handlers ---
  const handleAddParticipant = async (data: ParticipantCreate) => {
    try {
      await addParticipantMutation.mutateAsync({ tripId: tripId!, participant: data });
      toast.success('Participant added!');
      setAddParticipantModalOpen(false);
      participantForm.reset();
    } catch (error) {
      toast.error('Failed to add participant');
    }
  };

  const handleCreateDay = async (data: z.infer<typeof daySchema>) => {
    try {
      const dayData: ItineraryDayCreate = {
        date: data.date,
        title: data.title || null,
      };
      await createDayMutation.mutateAsync({ tripId: tripId!, day: dayData });
      toast.success('Day added to itinerary!');
      setAddDayModalOpen(false);
      dayForm.reset();
    } catch (error) {
      toast.error('Failed to add day');
    }
  };

  const handleAddActivity = async (data: ActivityFormData) => {
    if (!selectedDayId) return;
    try {
      // Transform form data to API format
      const activityData: ActivityCreate = {
        title: data.title,
        notes: data.notes || null,
        start_time: data.start_time || null,
        end_time: data.end_time || null,
        location: data.location || null,
      };
      await addActivityMutation.mutateAsync({ dayId: selectedDayId, activity: activityData, tripId: tripId! });
      toast.success('Activity added!');
      setAddActivityModalOpen(false);
      activityForm.reset();
    } catch (error) {
      toast.error('Failed to add activity');
    }
  };

  const handleCreatePoll = async (data: z.infer<typeof pollSchema>) => {
    try {
      const options = [data.option1, data.option2, data.option3, data.option4].filter(Boolean) as string[];
      const pollData: PollCreate = {
        question: data.question,
        options,
      };
      await createPollMutation.mutateAsync({ tripId: tripId!, poll: pollData });
      toast.success('Poll created!');
      setCreatePollModalOpen(false);
      pollForm.reset();
    } catch (error) {
      toast.error('Failed to create poll');
    }
  };

  const handleVote = async (optionId: string, participantId: string) => {
    try {
      const voteData: VoteCreate = { participant_id: participantId };
      await castVoteMutation.mutateAsync({ optionId, vote: voteData, tripId: tripId! });
      toast.success('Vote cast!');
    } catch (error) {
      toast.error('Failed to cast vote');
    }
  };

  const handleCreateExpense = async (data: ExpenseFormData) => {
    try {
      // Create equal splits among all participants
      const splits: ExpenseSplitBase[] = trip.participants.map(p => ({
        participant_id: p.id,
        owed_amount: data.amount / trip.participants.length,
      }));

      const expenseData: ExpenseCreate = {
        description: data.description,
        amount: data.amount,
        currency: data.currency,
        date: data.date,
        paid_by_id: data.paid_by_id,
        activity_id: null,
        splits,
      };

      await createExpenseMutation.mutateAsync({ tripId: tripId!, expense: expenseData });
      toast.success('Expense added!');
      setAddExpenseModalOpen(false);
      expenseForm.reset();
    } catch (error) {
      toast.error('Failed to add expense');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-4 md:p-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-3xl shadow-lg p-6 mb-6"
      >
        <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500">
          {trip.name}
        </h1>
        <p className="text-gray-600 mt-2">
          {trip.start_date && trip.end_date
            ? `${trip.start_date} - ${trip.end_date}`
            : 'Dates not set'}
        </p>
        <p className="text-sm text-gray-500 mt-1">Status: {trip.status}</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Participants Section */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-3xl shadow-lg p-6"
        >
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Participants</h2>
            <Button
              onClick={() => setAddParticipantModalOpen(true)}
              size="sm"
              className="bg-purple-600 hover:bg-purple-700 text-white"
            >
              + Add
            </Button>
          </div>
          <AnimatePresence>
            {trip.participants.map((participant) => (
              <motion.div
                key={participant.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-gray-50 rounded-xl p-4 mb-2"
              >
                <p className="font-semibold text-gray-800">{participant.name}</p>
                <p className="text-sm text-gray-600">{participant.email}</p>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>

        {/* Itinerary Section */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-3xl shadow-lg p-6"
        >
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Itinerary</h2>
            <Button
              onClick={() => setAddDayModalOpen(true)}
              size="sm"
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              + Add Day
            </Button>
          </div>
          <AnimatePresence>
            {trip.itinerary_days.map((day) => (
              <motion.div
                key={day.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mb-4 border-l-4 border-blue-500 pl-4"
              >
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <p className="font-bold text-gray-800">{day.date}</p>
                    {day.title && <p className="text-sm text-gray-600">{day.title}</p>}
                  </div>
                  <Button
                    onClick={() => {
                      setSelectedDayId(day.id);
                      setAddActivityModalOpen(true);
                    }}
                    size="sm"
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    + Activity
                  </Button>
                </div>
                {day.activities.map((activity) => (
                  <div key={activity.id} className="bg-gray-50 rounded-lg p-3 mb-2 ml-4">
                    <p className="font-semibold text-gray-800">{activity.title}</p>
                    {activity.location && <p className="text-sm text-gray-600">📍 {activity.location}</p>}
                    {activity.start_time && <p className="text-sm text-gray-600">🕐 {activity.start_time}</p>}
                  </div>
                ))}
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>

        {/* Polls Section */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-3xl shadow-lg p-6"
        >
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Polls</h2>
            <Button
              onClick={() => setCreatePollModalOpen(true)}
              size="sm"
              className="bg-indigo-600 hover:bg-indigo-700 text-white"
            >
              + Create Poll
            </Button>
          </div>
          <AnimatePresence>
            {trip.polls.map((poll) => (
              <motion.div
                key={poll.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-gray-50 rounded-xl p-4 mb-4"
              >
                <p className="font-bold text-gray-800 mb-3">{poll.question}</p>
                {poll.options.map((option) => (
                  <div key={option.id} className="bg-white rounded-lg p-3 mb-2 flex justify-between items-center">
                    <span className="text-gray-700">{option.content}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-semibold text-purple-600">{option.votes.length} votes</span>
                      {trip.participants.length > 0 && (
                        <Button
                          onClick={() => handleVote(option.id, trip.participants[0].id)}
                          size="sm"
                          className="bg-purple-600 hover:bg-purple-700 text-white"
                        >
                          Vote
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>

        {/* Expenses & Balance Section */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-3xl shadow-lg p-6"
        >
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Expenses</h2>
            <Button
              onClick={() => setAddExpenseModalOpen(true)}
              size="sm"
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              + Add Expense
            </Button>
          </div>

          {/* Balances */}
          {balances && balances.length > 0 && (
            <div className="mb-4 bg-yellow-50 rounded-xl p-4">
              <h3 className="font-bold text-gray-800 mb-2">Balances</h3>
              {balances.map((balance) => (
                <div key={balance.participant.id} className="flex justify-between items-center mb-1">
                  <span className="text-gray-700">{balance.participant.name}</span>
                  <span
                    className={`font-bold ${
                      balance.net_balance > 0 ? 'text-green-600' : balance.net_balance < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}
                  >
                    ${balance.net_balance.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Expense List */}
          <AnimatePresence>
            {trip.expenses.map((expense) => (
              <motion.div
                key={expense.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-gray-50 rounded-xl p-4 mb-2"
              >
                <p className="font-semibold text-gray-800">{expense.description}</p>
                <p className="text-sm text-gray-600">
                  ${expense.amount} {expense.currency} • {expense.date}
                </p>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Modals */}
      {isAddParticipantModalOpen && (
        <Modal onClose={() => setAddParticipantModalOpen(false)} title="Add Participant">
          <form onSubmit={participantForm.handleSubmit(handleAddParticipant)} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Name</label>
              <Input {...participantForm.register('name')} placeholder="Enter name" />
              {participantForm.formState.errors.name && (
                <p className="mt-1 text-sm text-red-600">{participantForm.formState.errors.name.message}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Email</label>
              <Input {...participantForm.register('email')} placeholder="Enter email" type="email" />
              {participantForm.formState.errors.email && (
                <p className="mt-1 text-sm text-red-600">{participantForm.formState.errors.email.message}</p>
              )}
            </div>
            <Button type="submit" className="w-full bg-purple-600 hover:bg-purple-700 text-white">
              Add Participant
            </Button>
          </form>
        </Modal>
      )}

      {isAddDayModalOpen && (
        <Modal onClose={() => setAddDayModalOpen(false)} title="Add Itinerary Day">
          <form onSubmit={dayForm.handleSubmit(handleCreateDay)} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Date</label>
              <Input {...dayForm.register('date')} type="date" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Title (Optional)</label>
              <Input {...dayForm.register('title')} placeholder="e.g., Arrival in Paris" />
            </div>
            <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white">
              Add Day
            </Button>
          </form>
        </Modal>
      )}

      {isAddActivityModalOpen && (
        <Modal onClose={() => setAddActivityModalOpen(false)} title="Add Activity">
          <form onSubmit={activityForm.handleSubmit(handleAddActivity)} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Title</label>
              <Input {...activityForm.register('title')} placeholder="e.g., Visit Eiffel Tower" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Location (Optional)</label>
              <Input {...activityForm.register('location')} placeholder="e.g., Paris, France" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Start Time (Optional)</label>
              <Input {...activityForm.register('start_time')} type="time" />
            </div>
            <Button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white">
              Add Activity
            </Button>
          </form>
        </Modal>
      )}

      {isCreatePollModalOpen && (
        <Modal onClose={() => setCreatePollModalOpen(false)} title="Create Poll">
          <form onSubmit={pollForm.handleSubmit(handleCreatePoll)} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Question</label>
              <Input {...pollForm.register('question')} placeholder="e.g., Where should we eat dinner?" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Option 1</label>
              <Input {...pollForm.register('option1')} placeholder="First option" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Option 2</label>
              <Input {...pollForm.register('option2')} placeholder="Second option" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Option 3 (Optional)</label>
              <Input {...pollForm.register('option3')} placeholder="Third option" />
            </div>
            <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">
              Create Poll
            </Button>
          </form>
        </Modal>
      )}

      {isAddExpenseModalOpen && (
        <Modal onClose={() => setAddExpenseModalOpen(false)} title="Add Expense">
          <form onSubmit={expenseForm.handleSubmit(handleCreateExpense)} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Description</label>
              <Input {...expenseForm.register('description')} placeholder="e.g., Dinner at restaurant" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Amount</label>
              <Input
                {...expenseForm.register('amount', { valueAsNumber: true })}
                type="number"
                step="0.01"
                placeholder="0.00"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Date</label>
              <Input {...expenseForm.register('date')} type="date" />
            </div>
            <input type="hidden" {...expenseForm.register('currency')} value="USD" />
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Paid By</label>
              <select {...expenseForm.register('paid_by_id')} className="w-full px-4 py-3 bg-white border-2 border-gray-200 rounded-xl">
                <option value="">Select participant</option>
                {trip.participants.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <Button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white">
              Add Expense
            </Button>
          </form>
        </Modal>
      )}
    </div>
  );
};

// Simple Modal Component
const Modal = ({ children, onClose, title }: { children: React.ReactNode; onClose: () => void; title: string }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-3xl shadow-2xl p-6 max-w-md w-full"
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-2xl font-bold text-gray-800">{title}</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl font-bold">
            ×
          </button>
        </div>
        {children}
      </motion.div>
    </div>
  );
};
