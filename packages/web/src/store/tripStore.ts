import { create } from 'zustand';

interface TripState {
  activeTripId: string | null;

  isCreatingNewTripModalOpen: boolean;
  isAddParticipantModalOpen: boolean;
  isCreateExpenseModalOpen: boolean;
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
  activeTripId: null,
  isCreatingNewTripModalOpen: false,
  isAddParticipantModalOpen: false,
  isCreateExpenseModalOpen: false,
  isCreatePollModalOpen: false,

  setActiveTripId: (tripId) => set({ activeTripId: tripId }),

  resetActiveTrip: () => set({ activeTripId: null }),
  
  setNewTripModalOpen: (isOpen) => set({ isCreatingNewTripModalOpen: isOpen }),

  setAddParticipantModalOpen: (isOpen) => set({ isAddParticipantModalOpen: isOpen }),

  setCreateExpenseModalOpen: (isOpen) => set({ isCreateExpenseModalOpen: isOpen }),

  setCreatePollModalOpen: (isOpen) => set({ isCreatePollModalOpen: isOpen }),
}));

