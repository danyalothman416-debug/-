import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { BottomNav } from './components/BottomNav';
import { AuthScreen } from './components/AuthScreen';
import { DashboardView } from './components/DashboardView';
import { DiseaseLibraryView } from './components/DiseaseLibraryView';
import { SymptomAnalyzerView } from './components/SymptomAnalyzerView';
import { LeveledQuizView } from './components/LeveledQuizView';
import { LabTestsView } from './components/LabTestsView';
import { PharmacologyView } from './components/PharmacologyView';
import { ClinicalCasesView } from './components/ClinicalCasesView';
import { CommunityChatView } from './components/CommunityChatView';
import { AiMedicalTutorView } from './components/AiMedicalTutorView';
import { AiVisionStudioView } from './components/AiVisionStudioView';
import { KurdistanSplashScreen } from './components/KurdistanSplashScreen';
import { GlobalSearchModal } from './components/GlobalSearchModal';
import { OnboardingProfileModal } from './components/OnboardingProfileModal';
import { ProfileAvatarModal } from './components/ProfileAvatarModal';
import { Sidebar } from './components/Sidebar';
import { PricingModal } from './components/PricingModal';
import { CheckoutModal } from './components/CheckoutModal';
import { DailyLimitReachedModal } from './components/DailyLimitReachedModal';
import { AdminVerificationView } from './components/AdminVerificationView';
import { HealthCalculatorsView } from './components/HealthCalculatorsView';
import { DailyHabitTrackerView } from './components/DailyHabitTrackerView';
import { VisualProgressTrackerView } from './components/VisualProgressTrackerView';
import { ProgressAnalyticsView } from './components/ProgressAnalyticsView';
import { QuickSupportWidget } from './components/QuickSupportWidget';
import { PwaInstallBanner } from './components/PwaInstallBanner';
import { Language, UserAccount, SubscriptionTier } from './types/medical';
import { AuthService } from './services/auth';
import { SubscriptionService } from './services/subscriptionService';
import { Activity, ShieldCheck, RefreshCw } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [language, setLanguage] = useState<Language>(() => {
    const saved = localStorage.getItem('dr_danyal_language');
    if (saved === 'ku' || saved === 'ar' || saved === 'en') return saved;
    return 'ku';
  });

  useEffect(() => {
    localStorage.setItem('dr_danyal_language', language);
    document.documentElement.lang = language;
    document.documentElement.dir = language === 'en' ? 'ltr' : 'rtl';
  }, [language]);
  const [currentUser, setCurrentUser] = useState<UserAccount | null>(null);
  const [pendingVerificationEmail, setPendingVerificationEmail] = useState<string | null>(null);
  
  // 🚨 قفڵەکە لێرەدا شکێنرا: true کرا بە false 🚨
  const [authLoading, setAuthLoading] = useState<boolean>(false);
  
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    const saved = localStorage.getItem('dr_danyal_theme');
    return saved ? saved === 'dark' : true;
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.add('light');
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('dr_danyal_theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  // Sidebar states
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);

  // Kurdistan Welcome Splash Screen & Global Search states
  const [showSplash, setShowSplash] = useState<boolean>(() => {
    return localStorage.getItem('dr_danyal_hide_splash') !== 'true';
  });
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false);
  const [skippedOnboarding, setSkippedOnboarding] = useState<boolean>(false);
  const [showProfileSetup, setShowProfileSetup] = useState<boolean>(false);
  const [showAvatarModal, setShowAvatarModal] = useState<boolean>(false);

  const [quizScore, setQuizScore] = useState<number>(0);
  const [streakDays, setStreakDays] = useState<number>(1);
  const [casesSolved, setCasesSolved] = useState<number>(0);

  // Subscription & Daily Limits state
  const [userTier, setUserTier] = useState<SubscriptionTier>(() => {
    return SubscriptionService.getCurrentTier();
  });
  const [isPricingOpen, setIsPricingOpen] = useState<boolean>(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState<boolean>(false);
  const [checkoutPlanId, setCheckoutPlanId] = useState<'pro' | 'vip'>('vip');
  const [isLimitModalOpen, setIsLimitModalOpen] = useState<boolean>(false);
  const [limitModalType, setLimitModalType] = useState<'consultation' | 'lab_scan' | 'image_gen' | 'pdf_export'>('consultation');

  // Sync subscription updates across app
  useEffect(() => {
    const unsub = SubscriptionService.subscribeToChanges((tier) => {
      setUserTier(tier);
    });
    return () => unsub();
  }, []);

  useEffect(() => {
    if (currentUser?.subscriptionTier) {
      setUserTier(currentUser.subscriptionTier);
    }
  }, [currentUser]);

  const handleOpenPricing = (planId?: 'pro' | 'vip') => {
    if (planId) {
      setCheckoutPlanId(planId);
      setIsCheckoutOpen(true);
    } else {
      setIsPricingOpen(true);
    }
  };

  const handleSelectPlanToUpgrade = (planId: 'pro' | 'vip') => {
    setIsPricingOpen(false);
    setCheckoutPlanId(planId);
    setIsCheckoutOpen(true);
  };

  const handleTriggerLimit = (type: 'consultation' | 'lab_scan' | 'image_gen' | 'pdf_export') => {
    setLimitModalType(type);
    setIsLimitModalOpen(true);
  };

  const handleUpgradeSuccess = (tier: SubscriptionTier) => {
    setUserTier(tier);
    if (currentUser) {
      setCurrentUser((prev) => prev ? { ...prev, subscriptionTier: tier, subscriptionStatus: 'active' } : null);
    }
  };

  const handleDemoUpgrade = async (tier: SubscriptionTier) => {
    await SubscriptionService.upgradeSubscription(tier, 'demo', `DEMO-${Date.now()}`);
    setUserTier(tier);
    if (currentUser) {
      setCurrentUser((prev) => prev ? { ...prev, subscriptionTier: tier, subscriptionStatus: 'active' } : null);
    }
  };

  // Global Shortcut for Command/Ctrl + K to open search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Subscribe to Firebase Auth State
  useEffect(() => {
    const unsubscribe = AuthService.onAuthStateChange((user, requiresVerification) => {
      setAuthLoading(false);
      if (user && !requiresVerification && user.emailVerified) {
        setCurrentUser(user);
        setPendingVerificationEmail(null);
        setQuizScore(user.quizScore || 0);
        setStreakDays(user.streakDays || 1);
        setCasesSolved(user.casesSolved || 0);
      } else if (user && requiresVerification) {
        // Block unverified user, keep pending verification email
        setCurrentUser(null);
        setPendingVerificationEmail(user.email);
      } else {
        setCurrentUser(null);
        setPendingVerificationEmail(null);
      }
    });

    return () => unsubscribe();
  }, []);

  // Whenever user progress updates, sync with Firestore via AuthService
  useEffect(() => {
    if (currentUser) {
      AuthService.updateProgress({ quizScore, streakDays, casesSolved });
    }
  }, [quizScore, streakDays, casesSolved, currentUser]);

  const handleAuthSuccess = (user: UserAccount) => {
    setCurrentUser(user);
    setPendingVerificationEmail(null);
    setQuizScore(user.quizScore || 0);
    setStreakDays(user.streakDays || 1);
    setCasesSolved(user.casesSolved || 0);
    setActiveTab('dashboard');
  };

  const handleLogout = async () => {
    await AuthService.logout();
    setCurrentUser(null);
    setPendingVerificationEmail(null);
  };

  const handleCaseSolved = () => {
    setCasesSolved((prev) => prev + 1);
    setQuizScore((prev) => prev + 50);
  };

  const isKu = language === 'ku';
  const isAr = language === 'ar';
  const isRtl = language === 'ku' || language === 'ar';

  // Loading screen while checking Firebase Auth state
  if (authLoading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-[#0c0926] via-[#140e3b] to-[#070518] text-white">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white mx-auto shadow-2xl shadow-cyan-500/30 animate-pulse">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <div className="flex items-center justify-center gap-2 text-cyan-400 text-sm font-semibold">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>{isKu ? 'دەستپێکردنی سیستەم...' : isAr ? 'جارٍ تحميل النظام...' : 'Connecting to Dr. Danyal Portal...'}</span>
          </div>
        </div>
      </div>
    );
  }

  // If user is not authenticated or unverified, render the sleek medical AuthScreen
  if (!currentUser) {
    return (
      <div dir={isRtl ? 'rtl' : 'ltr'} className={isRtl ? 'font-arabic' : 'font-sans'}>
        <AuthScreen
          language={language}
          setLanguage={setLanguage}
          onAuthSuccess={handleAuthSuccess}
          initialPendingVerificationEmail={pendingVerificationEmail}
        />
      </div>
    );
  }

  return (
    <div 
      dir={isRtl ? 'rtl' : 'ltr'} 
      data-theme={isDarkMode ? 'dark' : 'light'}
      className={`min-h-screen flex flex-col transition-colors duration-200 ${
        isDarkMode ? 'bg-[#090D16] text-[#F8FAFC]' : 'bg-[#F8FAFC] text-[#0F172A]'
      } ${
        isRtl ? 'font-arabic' : 'font-sans'
      }`}
    >
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={setLanguage}
        quizScore={quizScore}
        streakDays={streakDays}
        currentUser={currentUser}
        onLogout={handleLogout}
        isDarkMode={isDarkMode}
        setIsDarkMode={setIsDarkMode}
        userTier={userTier}
        onOpenPricing={handleOpenPricing}
        onOpenSearch={() => setIsSearchOpen(true)}
        onOpenSplash={() => setShowSplash(true)}
        onOpenProfile={() => setShowProfileSetup(true)}
        onOpenAvatarModal={() => setShowAvatarModal(true)}
        onToggleSidebar={() => {
          if (window.innerWidth >= 1280) {
            setSidebarCollapsed((prev) => !prev);
          } else {
            setSidebarOpen((prev) => !prev);
          }
        }}
      />

      {/* Main Layout Container with Modern Sidebar and Content Area */}
      <div className="flex-1 flex w-full relative min-h-0">
        {/* Modern Medical Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          language={language}
          setLanguage={setLanguage}
          currentUser={currentUser}
          quizScore={quizScore}
          streakDays={streakDays}
          casesSolved={casesSolved}
          onLogout={handleLogout}
          onOpenSearch={() => setIsSearchOpen(true)}
          onOpenSplash={() => setShowSplash(true)}
          onOpenProfile={() => setShowProfileSetup(true)}
          onOpenAvatarModal={() => setShowAvatarModal(true)}
          isOpen={sidebarOpen}
          setIsOpen={setSidebarOpen}
          isCollapsed={sidebarCollapsed}
          setIsCollapsed={setSidebarCollapsed}
          isDarkMode={isDarkMode}
          userTier={userTier}
          onOpenPricing={handleOpenPricing}
        />

        {/* Content Container (dynamically adjusted for desktop sidebar) */}
        <div 
          className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ease-in-out ${
            sidebarCollapsed 
              ? (isRtl ? 'xl:mr-20' : 'xl:ml-20') 
              : (isRtl ? 'xl:mr-72' : 'xl:ml-72')
          }`}
        >
          {/* Main Content Area */}
          <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-5 pb-24 md:pb-12">
            {activeTab === 'dashboard' && (
              <DashboardView
                language={language}
                setActiveTab={setActiveTab}
                quizScore={quizScore}
                streakDays={streakDays}
                casesSolved={casesSolved}
                currentUser={currentUser}
                onOpenAvatarModal={() => setShowAvatarModal(true)}
                userTier={userTier}
                onOpenPricing={handleOpenPricing}
              />
            )}

            {activeTab === 'diseases' && (
              <DiseaseLibraryView language={language} />
            )}

            {activeTab === 'symptom-analyzer' && (
              <SymptomAnalyzerView 
                language={language} 
                onNavigate={(tab) => setActiveTab(tab)}
              />
            )}

            {activeTab === 'labs' && (
              <LabTestsView 
                language={language}
                userTier={userTier}
                onOpenPricing={handleOpenPricing}
                onTriggerLimitReached={handleTriggerLimit}
                currentUser={currentUser}
              />
            )}

            {activeTab === 'pharmacology' && (
              <PharmacologyView language={language} />
            )}

            {activeTab === 'calculators' && (
              <HealthCalculatorsView language={language} />
            )}

            {activeTab === 'habit-tracker' && (
              <DailyHabitTrackerView language={language} />
            )}

            {activeTab === 'progress-tracker' && (
              <VisualProgressTrackerView 
                language={language}
                userTier={userTier}
                onOpenPricing={handleOpenPricing}
                onTriggerLimitReached={handleTriggerLimit}
              />
            )}

            {activeTab === 'analytics' && (
              <ProgressAnalyticsView language={language} />
            )}

            {activeTab === 'admin-panel' && (
              <AdminVerificationView 
                language={language}
                onPlanApproved={() => {
                  const curr = SubscriptionService.getCurrentTier();
                  setUserTier(curr);
                  if (currentUser) {
                    setCurrentUser((prev) => prev ? { ...prev, subscriptionTier: curr, subscriptionStatus: 'active' } : null);
                  }
                }}
              />
            )}

            {activeTab === 'quiz' && (
              <LeveledQuizView
                language={language}
                quizScore={quizScore}
                setQuizScore={setQuizScore}
                streakDays={streakDays}
              />
            )}

            {activeTab === 'cases' && (
              <ClinicalCasesView
                language={language}
                onCaseSolved={handleCaseSolved}
                currentUser={currentUser}
              />
            )}

            {activeTab === 'community' && (
              <CommunityChatView
                language={language}
                currentUser={currentUser}
              />
            )}

            {activeTab === 'ai-tutor' && (
              <AiMedicalTutorView 
                language={language} 
                userTier={userTier}
                onTriggerLimitReached={handleTriggerLimit}
                onOpenPricing={handleOpenPricing}
              />
            )}

            {activeTab === 'ai-vision-studio' && (
              <AiVisionStudioView 
                language={language} 
                userTier={userTier}
                onTriggerLimitReached={handleTriggerLimit}
                onOpenPricing={handleOpenPricing}
                currentUser={currentUser}
              />
            )}
          </main>

          {/* Clean Footer */}
          <footer className={`hidden md:block border-t py-5 px-4 text-xs mb-14 lg:mb-0 transition-colors ${
            isDarkMode 
              ? 'bg-[#090D16] border-slate-800/80 text-slate-400' 
              : 'bg-white border-slate-200 text-slate-600 shadow-xs'
          }`}>
            <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                <span className={`font-bold ${isDarkMode ? 'text-[#F8FAFC]' : 'text-[#0F172A]'}`}>Dr. Danyal Medical Trainer Pro Max</span>
                <span className="text-slate-500">•</span>
                <span className="text-[11px] text-emerald-500 font-semibold flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  {isKu ? 'هەژماری ڕێگەپێدراوی Firebase' : isAr ? 'محرك Firebase المعتمد والمرخص' : 'Verified Firebase Engine'}
                </span>
              </div>
              <div className={`${isDarkMode ? 'text-slate-400' : 'text-slate-500'} text-[11px]`}>
                {isKu
                  ? 'پەرەپێدراوە بۆ پێشخستنی زانستی پزیشکی و بڕیاردانی کلینیکی لە کوردستان و جیهان.'
                  : isAr
                  ? 'تم التطوير لدعم التفكير السريري القائم على الدليل والتعليم الطبي المتقدم في كردستان والعالم.'
                  : 'Evidence-based clinical reasoning and medical education for Kurdistan and globally.'}
              </div>
            </div>
          </footer>
        </div>
      </div>

      {/* Kurdistan Welcome Splash Screen Modal */}
      {showSplash && (
        <KurdistanSplashScreen
          language={language}
          setLanguage={setLanguage}
          onEnter={() => setShowSplash(false)}
        />
      )}

      {/* Global Unified Omni-Search Modal */}
      <GlobalSearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        language={language}
        onNavigate={(tab) => {
          setActiveTab(tab);
          setIsSearchOpen(false);
        }}
      />

      {/* Onboarding & Medical Profile Setup Modal */}
      {currentUser && ((!currentUser.departmentOrRole && !skippedOnboarding) || showProfileSetup) && (
        <OnboardingProfileModal
          currentUser={currentUser}
          language={language}
          onComplete={(updatedUser) => {
            setCurrentUser(updatedUser);
            setShowProfileSetup(false);
          }}
          onSkip={() => {
            setSkippedOnboarding(true);
            setShowProfileSetup(false);
          }}
        />
      )}

      {/* Profile Picture & Avatar Customizer Modal */}
      {currentUser && (
        <ProfileAvatarModal
          isOpen={showAvatarModal}
          onClose={() => setShowAvatarModal(false)}
          currentUser={currentUser}
          language={language}
          onUpdateUser={(updatedUser) => {
            setCurrentUser(updatedUser);
          }}
        />
      )}

      {/* Subscription Pricing Modal */}
      <PricingModal
        isOpen={isPricingOpen}
        onClose={() => setIsPricingOpen(false)}
        language={language}
        currentTier={userTier}
        onSelectPlanToUpgrade={handleSelectPlanToUpgrade}
        onDemoUpgrade={handleDemoUpgrade}
      />

      {/* Checkout & Payment Modal */}
      <CheckoutModal
        isOpen={isCheckoutOpen}
        onClose={() => setIsCheckoutOpen(false)}
        selectedPlanId={checkoutPlanId}
        onPlanChange={setCheckoutPlanId}
        language={language}
        onUpgradeSuccess={handleUpgradeSuccess}
      />

      {/* Daily Usage Limit Reached Modal */}
      <DailyLimitReachedModal
        isOpen={isLimitModalOpen}
        onClose={() => setIsLimitModalOpen(false)}
        onOpenUpgrade={(planId) => {
          setIsLimitModalOpen(false);
          handleOpenPricing(planId || 'vip');
        }}
        language={language}
        limitType={limitModalType}
      />

      {/* Quick WhatsApp & Telegram Clinical Support Widget */}
      <QuickSupportWidget language={language} />

      {/* PWA Home Screen Installation Banner */}
      <PwaInstallBanner language={language} />

      {/* Mobile-Friendly Fixed Bottom Navigation with AI Assistant */}
      <BottomNav
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        isDarkMode={isDarkMode}
      />
    </div>
  );
}
