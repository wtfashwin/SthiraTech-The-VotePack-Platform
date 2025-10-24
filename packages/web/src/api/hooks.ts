/**
 * TanStack Query hooks for server state management.
 * Each hook wraps an API service function and provides caching, loading, and error states.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tripService, itineraryService, pollingService, expenseService, authService, consensusService, importService, paymentService } from './apiClient';
import type {
  TripCreate,
  ParticipantCreate,
  ItineraryDayCreate,
  ActivityCreate,
  PollCreate,
  VoteCreate,
  ExpenseCreate,
  UserCreate,
  UserLogin,
  ImportFromUrlRequest,
  CommitmentDepositCreate,
} from '../types/db';

// --- Trip Hooks ---
export const useTrip = (tripId: string) => {
  return useQuery({
    queryKey: ['trip', tripId],
    queryFn: () => tripService.getTrip(tripId),
    enabled: !!tripId,
  });
};

export const useCreateTrip = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (trip: TripCreate) => tripService.createTrip(trip),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['trip', data.id] });
    },
  });
};

export const useAddParticipant = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ tripId, participant }: { tripId: string; participant: ParticipantCreate }) =>
      tripService.addParticipant(tripId, participant),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trip', variables.tripId] });
    },
  });
};

// --- Itinerary Hooks ---
export const useCreateItineraryDay = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ tripId, day }: { tripId: string; day: ItineraryDayCreate }) =>
      itineraryService.createItineraryDay(tripId, day),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trip', variables.tripId] });
    },
  });
};

export const useAddActivityToDay = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ dayId, activity, tripId }: { dayId: string; activity: ActivityCreate; tripId: string }) =>
      itineraryService.addActivityToDay(dayId, activity),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trip', variables.tripId] });
    },
  });
};

// --- Polling Hooks ---
export const useCreatePoll = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ tripId, poll }: { tripId: string; poll: PollCreate }) =>
      pollingService.createPoll(tripId, poll),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trip', variables.tripId] });
    },
  });
};

export const useCastVote = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ optionId, vote, tripId }: { optionId: string; vote: VoteCreate; tripId: string }) =>
      pollingService.castVote(optionId, vote),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trip', variables.tripId] });
    },
  });
};

// --- Expense Hooks ---
export const useCreateExpense = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ tripId, expense }: { tripId: string; expense: ExpenseCreate }) =>
      expenseService.createExpense(tripId, expense),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trip', variables.tripId] });
    },
  });
};

export const useTripBalance = (tripId: string) => {
  return useQuery({
    queryKey: ['balance', tripId],
    queryFn: () => expenseService.getTripBalance(tripId),
    enabled: !!tripId,
  });
};

// --- Authentication Hooks ---
export const useRegister = () => {
  return useMutation({
    mutationFn: (user: UserCreate) => authService.register(user),
  });
};

export const useLogin = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (credentials: UserLogin) => authService.login(credentials),
    onSuccess: (data) => {
      // Store token in localStorage
      localStorage.setItem('access_token', data.access_token);
      // Invalidate current user query to refetch
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });
};

export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => authService.getCurrentUser(),
    enabled: !!localStorage.getItem('access_token'),
    retry: false,
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => {
      authService.logout();
      return Promise.resolve();
    },
    onSuccess: () => {
      // Clear all queries
      queryClient.clear();
    },
  });
};

// --- AI Consensus Hooks ---
export const useConsensusProposals = (tripId: string) => {
  return useQuery({
    queryKey: ['consensus', tripId],
    queryFn: () => consensusService.getProposals(tripId),
    enabled: !!tripId,
  });
};

// --- URL Import Hooks ---
export const useImportFromUrl = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ tripId, request }: { tripId: string; request: ImportFromUrlRequest }) =>
      importService.importFromUrl(tripId, request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trip', variables.tripId] });
    },
  });
};

// --- Payment Hooks ---
export const useCreateCommitmentPayment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ tripId, deposit }: { tripId: string; deposit: CommitmentDepositCreate }) =>
      paymentService.createCommitmentPayment(tripId, deposit),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['deposits', variables.tripId] });
      queryClient.invalidateQueries({ queryKey: ['trip', variables.tripId] });
    },
  });
};

export const useTripDeposits = (tripId: string) => {
  return useQuery({
    queryKey: ['deposits', tripId],
    queryFn: () => paymentService.getTripDeposits(tripId),
    enabled: !!tripId,
  });
};

export const useCreateStripeOnboarding = () => {
  return useMutation({
    mutationFn: (participantId: string) => paymentService.createStripeOnboardingLink(participantId),
  });
};
