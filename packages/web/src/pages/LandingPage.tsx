import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

// Smooth scroll function
const scrollToSection = (id: string) => {
  const element = document.getElementById(id);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

// Navigation Component
const Navigation = () => {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-white/95 backdrop-blur-md shadow-lg' : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <svg
              className="w-10 h-10"
              viewBox="0 0 40 40"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="20" cy="20" r="18" fill="url(#gradient1)" />
              <path
                d="M20 10L25 18H15L20 10Z M15 22L20 30L25 22H15Z"
                fill="white"
              />
              <defs>
                <linearGradient
                  id="gradient1"
                  x1="0"
                  y1="0"
                  x2="40"
                  y2="40"
                >
                  <stop offset="0%" stopColor="#2563eb" />
                  <stop offset="100%" stopColor="#7c3aed" />
                </linearGradient>
              </defs>
            </svg>
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              SthiraTech
            </span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            {['Features', 'How it Works', 'Pricing'].map((item) => (
              <a
                key={item}
                href={`#${item.toLowerCase().replace(/\s+/g, '-')}`}
                onClick={(e) => {
                  e.preventDefault();
                  scrollToSection(item.toLowerCase().replace(/\s+/g, '-'));
                }}
                className="text-slate-700 hover:text-blue-600 font-medium transition-colors cursor-pointer"
              >
                {item}
              </a>
            ))}
            <button
              onClick={() => navigate('/register')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:shadow-lg hover:scale-105 transition-all duration-300"
            >
              Sign Up
            </button>
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

// Hero Section
const HeroSection = () => {
  const navigate = useNavigate();

  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20"
    >
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-100 via-purple-100 to-blue-100 opacity-50 animate-gradient-shift" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black leading-tight mb-6">
              Group Trips,{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Finally Organized.
              </span>
            </h1>
            <p className="text-xl sm:text-2xl text-slate-600 mb-8 leading-relaxed">
              Stop juggling chats, spreadsheets, and payment apps.{' '}
              <span className="font-semibold text-slate-800">PackVote 2.0</span>{' '}
              brings your entire group travel plan together.
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/register')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-4 rounded-xl text-lg font-bold shadow-2xl hover:shadow-purple-500/50 transition-all duration-300"
            >
              Get Started for Free
            </motion.button>
            <p className="text-sm text-slate-500 mt-4">
              ✓ No credit card required ✓ Free forever plan
            </p>
          </motion.div>

          {/* Right - Mock App UI */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="hidden lg:block"
          >
            <div className="bg-gradient-to-br from-slate-50 to-slate-200 rounded-3xl p-6 shadow-2xl relative">
              <div className="bg-white rounded-lg shadow-lg p-6 mb-4">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-500" />
                  <div>
                    <div className="h-3 w-32 bg-slate-200 rounded mb-2" />
                    <div className="h-2 w-24 bg-slate-100 rounded" />
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="h-4 bg-gradient-to-r from-blue-200 to-purple-200 rounded w-full" />
                  <div className="h-4 bg-slate-100 rounded w-3/4" />
                  <div className="h-4 bg-slate-100 rounded w-5/6" />
                </div>
              </div>
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="h-4 w-24 bg-blue-500 rounded" />
                  <div className="h-4 w-16 bg-purple-500 rounded" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="h-20 bg-gradient-to-br from-slate-100 to-slate-200 rounded-lg"
                    />
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

// Features Section
const FeaturesSection = () => {
  const features = [
    {
      icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
      title: 'Collaborative Itinerary',
      description:
        'Build your day-by-day plan together. Everyone contributes, everyone stays in sync. No more endless group chats.',
    },
    {
      icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
      title: 'In-App Polling',
      description:
        'Settle debates quickly with integrated polls. Beach A or Beach B? Let the group decide in seconds, not hours.',
    },
    {
      icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      title: 'Smart Expense Tracking',
      description:
        'Link costs to activities, see who owes whom instantly. No awkward money conversations, no spreadsheet gymnastics.',
    },
  ];

  return (
    <section id="features" className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl sm:text-5xl font-black mb-4">
            One App,{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Zero Hassle
            </span>
          </h2>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Everything you need to plan, decide, and settle up. All in one
            beautifully simple platform.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              className="bg-slate-50 rounded-2xl p-8 hover:transform hover:-translate-y-2 hover:shadow-2xl transition-all duration-300 border border-slate-200"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center mb-6">
                <svg
                  className="w-8 h-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d={feature.icon}
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4 text-slate-800">
                {feature.title}
              </h3>
              <p className="text-slate-600 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// How It Works Section
const HowItWorksSection = () => {
  const steps = [
    {
      number: '01',
      title: 'Create Trip',
      description:
        'Start your plan and invite your crew. Share a simple link and everyone joins instantly.',
      icon: 'M12 4v16m8-8H4',
    },
    {
      number: '02',
      title: 'Collaborate',
      description:
        'Build the itinerary and add activities together. Everyone can contribute ideas and suggestions.',
      icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    },
    {
      number: '03',
      title: 'Decide & Track',
      description:
        'Use polls for quick decisions, log expenses as you go. Real-time updates keep everyone informed.',
      icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
    },
    {
      number: '04',
      title: 'Settle Up',
      description:
        'See who owes whom and settle balances easily. Crystal-clear breakdowns eliminate confusion.',
      icon: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
    },
  ];

  return (
    <section
      id="how-it-works"
      className="py-24 bg-gradient-to-br from-slate-50 to-blue-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl sm:text-5xl font-black mb-4">
            How It{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Works
            </span>
          </h2>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Four simple steps to transform chaotic group planning into seamless
            collaboration.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="relative"
            >
              <div className="bg-white rounded-2xl p-8 hover:transform hover:-translate-y-2 hover:shadow-2xl transition-all duration-300 shadow-lg">
                <div className="text-6xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4 opacity-20">
                  {step.number}
                </div>
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
                  <svg
                    className="w-7 h-7 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d={step.icon}
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-3 text-slate-800">
                  {step.title}
                </h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  {step.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Testimonials Section
const TestimonialsSection = () => {
  const testimonials = [
    {
      quote:
        'PackVote completely changed how we plan our annual friend trips. No more endless WhatsApp threads!',
      author: 'Sarah Chen',
      trip: 'Bali Adventure 2024',
    },
    {
      quote:
        'The expense tracking is genius. We always struggled with splitting costs, but this made it effortless.',
      author: 'Marcus Johnson',
      trip: 'European Road Trip',
    },
    {
      quote:
        'Finally, one app that does everything. The polling feature saved us hours of debate about activities.',
      author: 'Priya Sharma',
      trip: 'Thailand Beach Getaway',
    },
  ];

  return (
    <section className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl sm:text-5xl font-black mb-4">
            Don't Just Take{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Our Word
            </span>
          </h2>
          <p className="text-xl text-slate-600">
            Thousands of travelers are already planning better together.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8 hover:transform hover:-translate-y-2 hover:shadow-2xl transition-all duration-300 border border-blue-100"
            >
              <svg
                className="w-10 h-10 text-blue-500 mb-4 opacity-50"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
              </svg>
              <p className="text-slate-700 text-lg mb-6 leading-relaxed italic">
                "{testimonial.quote}"
              </p>
              <div>
                <p className="font-bold text-slate-800">{testimonial.author}</p>
                <p className="text-sm text-slate-500">{testimonial.trip}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Pricing Section
const PricingSection = () => {
  const navigate = useNavigate();

  const plans = [
    {
      name: 'Free',
      price: '$0',
      features: [
        'Up to 3 trips',
        'Unlimited collaborators',
        'Basic expense tracking',
        'Community support',
      ],
    },
    {
      name: 'Pro',
      price: '$9',
      features: [
        'Unlimited trips',
        'Advanced analytics',
        'Priority support',
        'Custom branding',
      ],
      highlight: true,
    },
    {
      name: 'Team',
      price: '$29',
      features: [
        'Everything in Pro',
        'Team management',
        'API access',
        'Dedicated support',
      ],
    },
  ];

  return (
    <section
      id="pricing"
      className="py-24 bg-gradient-to-br from-slate-50 to-purple-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <h2 className="text-4xl sm:text-5xl font-black mb-4">
            Simple,{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Transparent Pricing
            </span>
          </h2>
          <p className="text-xl text-slate-600 mb-12 max-w-2xl mx-auto">
            Start free, upgrade when you need more power. No hidden fees, ever.
          </p>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {plans.map((plan, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.15 }}
                className={`bg-white rounded-2xl p-8 hover:transform hover:-translate-y-2 hover:shadow-2xl transition-all duration-300 ${
                  plan.highlight
                    ? 'ring-4 ring-blue-500 shadow-2xl scale-105'
                    : 'shadow-lg'
                }`}
              >
                {plan.highlight && (
                  <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-bold px-4 py-1 rounded-full inline-block mb-4">
                    MOST POPULAR
                  </div>
                )}
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="mb-6">
                  <span className="text-5xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {plan.price}
                  </span>
                  <span className="text-slate-600">/month</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center text-slate-600">
                      <svg
                        className="w-5 h-5 text-green-500 mr-2"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => navigate('/register')}
                  className={`w-full py-3 rounded-lg font-semibold transition-all ${
                    plan.highlight
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg hover:scale-105'
                      : 'bg-slate-100 text-slate-800 hover:bg-slate-200'
                  }`}
                >
                  Get Started
                </button>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

// Final CTA Section
const FinalCTASection = () => {
  const navigate = useNavigate();

  return (
    <section
      id="cta-final"
      className="py-24 bg-gradient-to-br from-blue-600 via-purple-600 to-blue-700 text-white relative overflow-hidden"
    >
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-96 h-96 bg-white rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-300 rounded-full blur-3xl" />
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black mb-6 leading-tight">
            Ready to End Group Travel Chaos?
          </h2>
          <p className="text-xl sm:text-2xl mb-10 opacity-90 leading-relaxed">
            Join thousands of travelers who plan better together. Start your
            first trip today, completely free.
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/register')}
            className="bg-white text-blue-600 px-12 py-5 rounded-xl text-xl font-bold shadow-2xl hover:shadow-white/50 transition-all duration-300 inline-block"
          >
            Sign Up Free & Start Planning
          </motion.button>
          <p className="text-sm mt-6 opacity-75">
            ✓ No credit card required ✓ 2-minute setup ✓ Cancel anytime
          </p>
        </motion.div>
      </div>
    </section>
  );
};

// Footer
const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-slate-900 text-slate-400 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Company */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <svg
                className="w-8 h-8"
                viewBox="0 0 40 40"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle cx="20" cy="20" r="18" fill="url(#gradient2)" />
                <path
                  d="M20 10L25 18H15L20 10Z M15 22L20 30L25 22H15Z"
                  fill="white"
                />
                <defs>
                  <linearGradient
                    id="gradient2"
                    x1="0"
                    y1="0"
                    x2="40"
                    y2="40"
                  >
                    <stop offset="0%" stopColor="#2563eb" />
                    <stop offset="100%" stopColor="#7c3aed" />
                  </linearGradient>
                </defs>
              </svg>
              <span className="text-xl font-bold text-white">SthiraTech</span>
            </div>
            <p className="text-sm">
              Making group travel planning effortless, one trip at a time.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-white font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-sm">
              {['Features', 'Pricing', 'Roadmap', 'Updates'].map((item) => (
                <li key={item}>
                  <a href="#" className="hover:text-white transition-colors">
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-white font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm">
              {['About', 'Blog', 'Careers', 'Contact'].map((item) => (
                <li key={item}>
                  <a href="#" className="hover:text-white transition-colors">
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              {['Privacy Policy', 'Terms of Service', 'Cookie Policy', 'GDPR'].map(
                (item) => (
                  <li key={item}>
                    <a href="#" className="hover:text-white transition-colors">
                      {item}
                    </a>
                  </li>
                )
              )}
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm">
            © {currentYear} SthiraTech. All rights reserved.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            {['Twitter', 'LinkedIn', 'Instagram'].map((social) => (
              <a
                key={social}
                href="#"
                className="hover:text-white transition-colors text-sm"
              >
                {social}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
};

// Main Landing Page Component
export default function LandingPage() {
  return (
    <div className="overflow-x-hidden">
      <Navigation />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <TestimonialsSection />
      <PricingSection />
      <FinalCTASection />
      <Footer />
    </div>
  );
}
