/**
 * ConsensusProposalsCard - AI-powered consensus proposals component
 * Displays scored itinerary proposals based on group preferences
 */
import { motion } from 'framer-motion';
import { useConsensusProposals } from '../api/hooks';
import { Button } from './ui/button';
import type { ConsensusProposal } from '../types/db';

interface ConsensusProposalsCardProps {
  tripId: string;
}

export const ConsensusProposalsCard = ({ tripId }: ConsensusProposalsCardProps) => {
  const { data: consensusData, isLoading, error, refetch } = useConsensusProposals(tripId);

  if (isLoading) {
    return (
      <div className="bg-white rounded-3xl shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-3xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-3">AI Consensus Proposals</h3>
        <p className="text-red-600">Failed to load proposals. Try again later.</p>
        <Button onClick={() => refetch()} className="mt-3 bg-purple-600 hover:bg-purple-700 text-white">
          Retry
        </Button>
      </div>
    );
  }

  if (!consensusData || consensusData.proposals.length === 0) {
    return (
      <div className="bg-white rounded-3xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-3">AI Consensus Proposals</h3>
        <p className="text-gray-600 mb-3">
          No proposals available yet. Make sure participants have filled out their survey responses.
        </p>
        <Button onClick={() => refetch()} className="bg-purple-600 hover:bg-purple-700 text-white">
          Generate Proposals
        </Button>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-orange-600';
  };

  const getPaceBadgeColor = (pace: string) => {
    if (pace === 'relaxed') return 'bg-blue-100 text-blue-800';
    if (pace === 'moderate') return 'bg-purple-100 text-purple-800';
    if (pace === 'packed') return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-3xl shadow-lg p-6"
    >
      <div className="flex justify-between items-center mb-4">
        <div>
          <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600">
            🤖 AI Consensus Proposals
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {consensusData.group_size} participants • Avg budget: ${consensusData.average_budget?.toFixed(0) || 'N/A'}
          </p>
        </div>
        <Button onClick={() => refetch()} size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-white">
          Refresh
        </Button>
      </div>

      <div className="space-y-4">
        {consensusData.proposals.map((proposal: ConsensusProposal, index: number) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-2xl p-5 shadow-md hover:shadow-lg transition-shadow"
          >
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl">{index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}</span>
                  <h4 className="text-lg font-bold text-gray-800">{proposal.title}</h4>
                </div>
                <p className="text-sm text-gray-600 mb-2">{proposal.description}</p>
              </div>
              <div className="text-right ml-4">
                <div className={`text-3xl font-black ${getScoreColor(proposal.score)}`}>
                  {proposal.score.toFixed(0)}
                </div>
                <div className="text-xs text-gray-500">score</div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-3">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getPaceBadgeColor(proposal.pace)}`}>
                {proposal.pace.charAt(0).toUpperCase() + proposal.pace.slice(1)} Pace
              </span>
              {proposal.estimated_budget && (
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                  ${proposal.estimated_budget.toFixed(0)} per person
                </span>
              )}
            </div>

            <div className="bg-gray-50 rounded-xl p-3 mb-3">
              <p className="text-sm text-gray-700 italic">{proposal.justification}</p>
            </div>

            <div>
              <p className="text-xs font-semibold text-gray-600 mb-2">Included Activities:</p>
              <ul className="space-y-1">
                {proposal.activities.map((activity, actIndex) => (
                  <li key={actIndex} className="text-sm text-gray-700 flex items-start">
                    <span className="text-purple-500 mr-2">•</span>
                    {activity}
                  </li>
                ))}
              </ul>
            </div>

            <div className="mt-4 flex gap-2">
              <Button size="sm" className="flex-1 bg-purple-600 hover:bg-purple-700 text-white">
                Discuss
              </Button>
              <Button size="sm" className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800">
                Customize
              </Button>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};
