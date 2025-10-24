/**
 * CommitmentSection - Stripe-powered commitment deposit management
 * Displays commitment requirements and payment status for trip participants
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { useTripDeposits } from '../api/hooks';
import { Button } from './ui/button';
import type { TripPublic } from '../types/db';

interface CommitmentSectionProps {
  trip: TripPublic;
  onCommitClick: () => void;
}

export const CommitmentSection = ({ trip, onCommitClick }: CommitmentSectionProps) => {
  const { data: deposits, isLoading } = useTripDeposits(trip.id);
  const [showDetails, setShowDetails] = useState(false);

  // Check if commitment is enabled for this trip
  if (!trip.commitment_amount || trip.commitment_amount <= 0) {
    return null;
  }

  // Calculate payment statistics
  const totalParticipants = trip.participants.length;
  const paidDeposits = deposits?.filter(d => d.status === 'paid').length || 0;
  const pendingDeposits = deposits?.filter(d => d.status === 'pending').length || 0;
  const paymentRate = totalParticipants > 0 ? (paidDeposits / totalParticipants) * 100 : 0;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-3xl shadow-lg p-6"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-emerald-600">
            💰 Commitment Deposits
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Secure your spot with a ${trip.commitment_amount.toFixed(2)} {trip.commitment_currency} deposit
          </p>
        </div>
        <Button
          onClick={onCommitClick}
          size="sm"
          className="bg-green-600 hover:bg-green-700 text-white"
        >
          Pay Deposit
        </Button>
      </div>

      {/* Payment Progress */}
      <div className="bg-white rounded-2xl p-4 mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-semibold text-gray-700">Payment Progress</span>
          <span className="text-sm font-bold text-green-600">{paidDeposits}/{totalParticipants} paid</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${paymentRate}%` }}
            transition={{ duration: 0.5 }}
            className="bg-gradient-to-r from-green-500 to-emerald-500 h-full rounded-full"
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">{paymentRate.toFixed(0)}% commitment rate</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-white rounded-xl p-3 text-center">
          <div className="text-2xl font-black text-green-600">{paidDeposits}</div>
          <div className="text-xs text-gray-600">Paid</div>
        </div>
        <div className="bg-white rounded-xl p-3 text-center">
          <div className="text-2xl font-black text-yellow-600">{pendingDeposits}</div>
          <div className="text-xs text-gray-600">Pending</div>
        </div>
        <div className="bg-white rounded-xl p-3 text-center">
          <div className="text-2xl font-black text-gray-600">{totalParticipants - paidDeposits - pendingDeposits}</div>
          <div className="text-xs text-gray-600">Not Started</div>
        </div>
      </div>

      {/* Toggle Details */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="w-full text-sm text-purple-600 hover:text-purple-700 font-semibold mb-2"
      >
        {showDetails ? '▼ Hide Details' : '▶ Show Participant Details'}
      </button>

      {/* Participant Details */}
      {showDetails && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="space-y-2"
        >
          {isLoading ? (
            <div className="text-center py-4 text-gray-500">Loading deposit details...</div>
          ) : (
            trip.participants.map((participant) => {
              const deposit = deposits?.find(d => d.participant_id === participant.id);
              const status = deposit?.status || 'not_started';
              
              return (
                <div key={participant.id} className="bg-white rounded-xl p-3 flex justify-between items-center">
                  <div>
                    <p className="font-semibold text-gray-800">{participant.name}</p>
                    <p className="text-xs text-gray-500">{participant.email}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {deposit && (
                      <span className="text-sm font-semibold text-gray-700">
                        ${deposit.amount.toFixed(2)}
                      </span>
                    )}
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(status)}`}>
                      {status === 'not_started' ? 'Not Paid' : status.charAt(0).toUpperCase() + status.slice(1)}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </motion.div>
      )}

      {/* Info Banner */}
      <div className="mt-4 bg-blue-50 border-l-4 border-blue-500 p-3 rounded">
        <p className="text-xs text-blue-800">
          <strong>Why deposits?</strong> Commitment deposits help ensure everyone is serious about the trip, 
          reducing last-minute dropouts and making planning more reliable for the group.
        </p>
      </div>
    </motion.div>
  );
};
