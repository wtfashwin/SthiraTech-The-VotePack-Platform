/**
 * API Client for the PackVote backend.
 * All API calls are defined here with proper TypeScript typing.
 */
import axios from 'axios';
import type {
  TripCreate,
  TripPublic,
  ParticipantCreate,
  ParticipantPublic,
  ItineraryDayCreate,
  ItineraryDayPublic,
  ActivityCreate,
  ActivityPublic,
  PollCreate,
  PollPublic,
  VoteCreate,
  VotePublic,
  ExpenseCreate,
  ExpensePublic,
  Balance,
  UserCreate,
  UserLogin,
  UserPublic,
  Token,
} from '../types/db';

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // baseURL is correct for Axios
  headers: {
    'Content-Type': 'application/json',
  },
} as any); // Type assertion to resolve incorrect type definition

// Add request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// --- Trip Services ---
export const tripService = {
  createTrip: async (trip: TripCreate): Promise<TripPublic> => {
    const { data } = await apiClient.post<TripPublic>('/trips', trip);
    return data;
  },

  getTrip: async (tripId: string): Promise<TripPublic> => {
    const { data } = await apiClient.get<TripPublic>(`/${tripId}`);
    return data;
  },

  addParticipant: async (tripId: string, participant: ParticipantCreate): Promise<ParticipantPublic> => {
    const { data } = await apiClient.post<ParticipantPublic>(`/${tripId}/participants/`, participant);
    return data;
  },
};

// --- Itinerary Services ---
export const itineraryService = {
  createItineraryDay: async (tripId: string, day: ItineraryDayCreate): Promise<ItineraryDayPublic> => {
    const { data } = await apiClient.post<ItineraryDayPublic>(`/itinerary/trips/${tripId}/days/`, day);
    return data;
  },

  addActivityToDay: async (dayId: string, activity: ActivityCreate): Promise<ActivityPublic> => {
    const { data} = await apiClient.post<ActivityPublic>(`/itinerary/days/${dayId}/activities/`, activity);
    return data;
  },
};

// --- Polling Services ---
export const pollingService = {
  createPoll: async (tripId: string, poll: PollCreate): Promise<PollPublic> => {
    const { data } = await apiClient.post<PollPublic>(`/trips/${tripId}/polls/`, poll);
    return data;
  },

  castVote: async (optionId: string, vote: VoteCreate): Promise<VotePublic> => {
    const { data } = await apiClient.post<VotePublic>(`/polls/options/${optionId}/vote`, vote);
    return data;
  },
};

// --- Expense Services ---
export const expenseService = {
  createExpense: async (tripId: string, expense: ExpenseCreate): Promise<ExpensePublic> => {
    const { data } = await apiClient.post<ExpensePublic>(`/trips/${tripId}/expenses/`, expense);
    return data;
  },

  getTripBalance: async (tripId: string): Promise<Balance[]> => {
    const { data } = await apiClient.get<Balance[]>(`/trips/${tripId}/expenses/balance/`);
    return data;
  },
};

// --- Authentication Services ---
export const authService = {
  register: async (user: UserCreate): Promise<UserPublic> => {
    const { data } = await apiClient.post<UserPublic>('/auth/register', user);
    return data;
  },

  login: async (credentials: UserLogin): Promise<Token> => {
    // OAuth2PasswordRequestForm expects form data, not JSON
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);
    
    const { data } = await axios.post<Token>(
      'http://localhost:8000/api/v1/auth/login',
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    return data;
  },

  getCurrentUser: async (): Promise<UserPublic> => {
    const { data } = await apiClient.get<UserPublic>('/auth/me');
    return data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
  },
};

export default apiClient;
