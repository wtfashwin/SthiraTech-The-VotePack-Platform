import { create } from 'zustand';

interface TripState {
  // --- Core Trip Selection ---
  /** The ID of the trip currently active in the UI. Used by TanStack Query hooks. */
  activeTripId: string | null;

  // --- UI/Modal States ---
  /** Whether the modal for creating a new trip is open. */
  isCreatingNewTripModalOpen: boolean;
  /** Whether the modal for adding participants is open. */
  isAddParticipantModalOpen: boolean;
  /** Whether the modal for creating an expense is open. */
  isCreateExpenseModalOpen: boolean;
  /** Whether the modal for creating a poll is open. */
  isCreatePollModalOpen: boolean;
  
  // --- Actions ---
  setActiveTripId: (tripId: string | null) => void;
  resetActiveTrip: () => void;
  
  // Modal Toggles
  setNewTripModalOpen: (isOpen: boolean) => void;
  setAddParticipantModalOpen: (isOpen: boolean) => void;
  setCreateExpenseModalOpen: (isOpen: boolean) => void;
  setCreatePollModalOpen: (isOpen: boolean) => void;
}

export const useTripStore = create<TripState>((set) => ({
  // --- Initial State ---
  activeTripId: null,
  isCreatingNewTripModalOpen: false,
  isAddParticipantModalOpen: false,
  isCreateExpenseModalOpen: false,
  isCreatePollModalOpen: false,

  // --- Actions Implementation ---
  setActiveTripId: (tripId) => set({ activeTripId: tripId }),

  resetActiveTrip: () => set({ activeTripId: null }),
  
  setNewTripModalOpen: (isOpen) => set({ isCreatingNewTripModalOpen: isOpen }),

  setAddParticipantModalOpen: (isOpen) => set({ isAddParticipantModalOpen: isOpen }),

  setCreateExpenseModalOpen: (isOpen) => set({ isCreateExpenseModalOpen: isOpen }),

  setCreatePollModalOpen: (isOpen) => set({ isCreatePollModalOpen: isOpen }),
}));

