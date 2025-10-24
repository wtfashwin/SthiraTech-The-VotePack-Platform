/**
 * TypeScript types matching the backend Pydantic schemas.
 * These interfaces use snake_case to match the API responses exactly.
 */

// --- Enums ---
export enum TripStatus {
  PLANNING = "PLANNING",
  CONFIRMED = "CONFIRMED",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETED = "COMPLETED",
  ARCHIVED = "ARCHIVED"
}

// --- User Types ---
export interface UserPublic {
  id: string;
  email: string;
  name: string | null;
}

export interface UserCreate {
  email: string;
  password: string;
  name?: string | null;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

// --- Participant Types ---
export interface ParticipantBase {
  name: string;
  email: string;
}

export interface ParticipantCreate extends ParticipantBase {}

export interface ParticipantPublic extends ParticipantBase {
  id: string;
  trip_id: string;
}

// --- Trip Types ---
export interface TripBase {
  name: string;
  start_date: string | null;
  end_date: string | null;
}

export interface TripCreate extends TripBase {
  participants: ParticipantCreate[];
}

export interface TripPublic extends TripBase {
  id: string;
  creator_id: string;
  status: TripStatus;
  final_destination: string | null;
  participants: ParticipantPublic[];
  recommendations: RecommendationPublic[];
  itinerary_days: ItineraryDayPublic[];
  polls: PollPublic[];
  expenses: ExpensePublic[];
}

// --- Recommendation Types ---
export interface RecommendationPublic {
  id: string;
  destination_name: string;
  description: string | null;
}

// --- Itinerary Types ---
export interface ItineraryDayBase {
  date: string;
  title: string | null;
}

export interface ItineraryDayCreate extends ItineraryDayBase {}

export interface ItineraryDayPublic extends ItineraryDayBase {
  id: string;
  activities: ActivityPublic[];
}

// --- Activity Types ---
export interface ActivityBase {
  title: string;
  notes: string | null;
  start_time: string | null;
  end_time: string | null;
  location: string | null;
}

export interface ActivityCreate extends ActivityBase {}

export interface ActivityPublic extends ActivityBase {
  id: string;
  expense: ExpensePublic | null;
}

// --- Poll Types ---
export interface PollBase {
  question: string;
}

export interface PollCreate extends PollBase {
  options: string[];
}

export interface PollPublic extends PollBase {
  id: string;
  is_active: boolean;
  options: PollOptionPublic[];
}

export interface PollOptionPublic {
  id: string;
  content: string;
  votes: VotePublic[];
}

export interface VoteCreate {
  participant_id: string;
}

export interface VotePublic {
  id: string;
  participant_id: string;
}

// --- Expense Types ---
export interface ExpenseSplitBase {
  participant_id: string;
  owed_amount: number;
}

export interface ExpenseSplitPublic extends ExpenseSplitBase {
  id: string;
  is_settled: boolean;
}

export interface ExpenseBase {
  description: string;
  amount: number;
  currency: string;
  date: string;
  paid_by_id: string;
  activity_id: string | null;
}

export interface ExpenseCreate extends ExpenseBase {
  splits: ExpenseSplitBase[];
}

export interface ExpensePublic extends ExpenseBase {
  id: string;
  splits: ExpenseSplitPublic[];
}

// --- Balance Types ---
export interface Balance {
  participant: ParticipantPublic;
  net_balance: number;
}
