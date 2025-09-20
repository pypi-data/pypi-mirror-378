import React, { useState, useEffect, useCallback } from 'react';
import { AuthService } from './auth';
import {
  TrainwaveUser,
  Job,
  JobStatus,
  TrainwaveApiClient
} from './api-client';
import { requestAPI } from './handler';
import { showJobNameDialog } from './job-name-dialog';

// Icon components matching the web app
const HiCheckCircle = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="currentColor"
    viewBox="0 0 20 20"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      fillRule="evenodd"
      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
      clipRule="evenodd"
    />
  </svg>
);

const HiMiniXCircle = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="currentColor"
    viewBox="0 0 20 20"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      fillRule="evenodd"
      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
      clipRule="evenodd"
    />
  </svg>
);

const HiOutlineArrowPath = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
    />
  </svg>
);

const HiMiniQuestionMarkCircle = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    className={className}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M12 9v3.75m0-10.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.75c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.57-.598-3.75h-.152c-3.196 0-6.1-1.25-8.25-3.286Zm0 13.036h.008v.008H12v-.008Z"
    />
  </svg>
);

const HiStopCircle = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="currentColor"
    viewBox="0 0 20 20"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      fillRule="evenodd"
      d="M2 10a8 8 0 1116 0 8 8 0 01-16 0zm5-3.25A.75.75 0 017.75 6h4.5a.75.75 0 01.75.75v6.5a.75.75 0 01-.75.75h-4.5a.75.75 0 01-.75-.75v-6.5z"
      clipRule="evenodd"
    />
  </svg>
);

const HiCodeBracketSquare = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M14.25 9.75L16.5 12l-2.25 2.25m-4.5 0L7.5 12l2.25-2.25M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z"
    />
  </svg>
);

const HiClock = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  </svg>
);

const HiMiniMinusCircle = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="currentColor"
    viewBox="0 0 20 20"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      fillRule="evenodd"
      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM6.75 9.25a.75.75 0 000 1.5h6.5a.75.75 0 000-1.5h-6.5z"
      clipRule="evenodd"
    />
  </svg>
);

interface DropdownProps {
  authService: AuthService;
  onSettingsClick: () => void;
  onLoginClick?: () => void;
  notebookTracker?: any; // INotebookTracker from JupyterLab
}

// Use the Job interface from api-client.ts

export const TrainwaveDropdown: React.FC<DropdownProps> = ({
  authService,
  onSettingsClick,
  onLoginClick,
  notebookTracker
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState<TrainwaveUser | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLaunchingJob, setIsLaunchingJob] = useState(false);
  const [apiClient, setApiClient] = useState<TrainwaveApiClient | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // Function to refresh the dropdown state
  const refreshDropdown = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  // Expose refresh function globally
  useEffect(() => {
    (window as any).refreshTrainwaveDropdown = refreshDropdown;
    return () => {
      delete (window as any).refreshTrainwaveDropdown;
    };
  }, []);

  useEffect(() => {
    if (authService.isAuthenticated()) {
      setUser(authService.getUser());
      const client = authService.getApiClient();
      setApiClient(client);
      loadJobs(client);
    } else {
      setUser(null);
      setJobs([]);
      setApiClient(null);
    }
  }, [authService, refreshTrigger]);

  // Polling effect for jobs
  useEffect(() => {
    if (!authService.isAuthenticated() || !apiClient) {
      return;
    }

    const pollInterval = setInterval(() => {
      loadJobs(apiClient, true); // Pass isPolling=true to avoid loading spinner
    }, 10000); // Poll every 10 seconds

    return () => clearInterval(pollInterval);
  }, [authService, apiClient]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (isOpen && !target.closest('.trainwave-dropdown-container')) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () =>
        document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const loadJobs = async (client: TrainwaveApiClient, isPolling = false) => {
    // Only show loading spinner on initial load, not during polling
    if (!isPolling) {
      setIsLoading(true);
    }
    try {
      const settings = authService.loadSettings();
      const jobsData = await client.listJobs(
        settings.organization_id,
        settings.project_id
      );
      setJobs(jobsData);
      setIsInitialLoad(false);
    } catch (error) {
      console.error('Failed to load jobs:', error);
      // Keep existing jobs on error to avoid flickering
    } finally {
      if (!isPolling) {
        setIsLoading(false);
      }
    }
  };

  const formatTimeAgo = useCallback((dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else {
      return `${diffDays}d ago`;
    }
  }, []);

  const getStatusIcon = (status: JobStatus): React.ReactElement | null => {
    switch (status) {
      case JobStatus.SUBMIT_CODE:
        return (
          <HiCodeBracketSquare className="trainwave-icon trainwave-icon-pink" />
        );
      case JobStatus.LAUNCHING:
        return (
          <HiOutlineArrowPath className="trainwave-icon trainwave-icon-cyan trainwave-icon-spin" />
        );
      case JobStatus.RUNNING:
        return (
          <HiOutlineArrowPath className="trainwave-icon trainwave-icon-blue trainwave-icon-spin" />
        );
      case JobStatus.SUCCESS:
        return (
          <HiCheckCircle className="trainwave-icon trainwave-icon-green" />
        );
      case JobStatus.ERROR:
        return (
          <HiMiniMinusCircle className="trainwave-icon trainwave-icon-orange" />
        );
      case JobStatus.SYSTEM_TERMINATED:
        return <HiClock className="trainwave-icon trainwave-icon-orange" />;
      case JobStatus.USER_CANCELLED:
        return <HiStopCircle className="trainwave-icon trainwave-icon-gray" />;
      case JobStatus.USER_PROCESS_FAILED:
        return <HiMiniXCircle className="trainwave-icon trainwave-icon-red" />;
      default:
        return (
          <HiMiniQuestionMarkCircle className="trainwave-icon trainwave-icon-gray" />
        );
    }
  };

  const activeJobs = jobs.filter(
    job =>
      job.state === JobStatus.RUNNING ||
      job.state === JobStatus.SUBMIT_CODE ||
      job.state === JobStatus.LAUNCHING
  );
  const hasActiveJobs = activeJobs.length > 0;

  // Memoized job item component to prevent unnecessary re-renders
  const JobItem = React.memo(({ job }: { job: Job }) => (
    <div className="trainwave-job-item">
      <div className="trainwave-job-header">
        <span className="trainwave-job-status">{getStatusIcon(job.state)}</span>
        <div className="trainwave-job-info">
          <span className="trainwave-job-name">
            <a
              href={`https://trainwave.ai/jobs/${job.id}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {job.config.name}
            </a>
          </span>
          <div className="trainwave-job-meta">
            <a
              href={`https://trainwave.ai/projects/${job.project.id}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <span className="trainwave-job-type">{job.project.name}</span>
            </a>
            <span className="trainwave-job-gpu">
              {job.cloud_offer.gpu_type || 'CPU'}
            </span>
          </div>
        </div>
        <span className="trainwave-job-time">
          {formatTimeAgo(job.created_at)}
        </span>
      </div>
    </div>
  ));

  // const handleLogout = async () => {
  //   try {
  //     await authService.logout();
  //     setIsOpen(false);
  //   } catch (error) {
  //     console.error('Logout failed:', error);
  //   }
  // };

  return (
    <div className="trainwave-dropdown-container">
      <div
        className="trainwave-dropdown-trigger"
        onClick={() => {
          setIsOpen(!isOpen);
        }}
      >
        {hasActiveJobs && (
          <div className="trainwave-job-running-indicator"></div>
        )}
        <span className="trainwave-dropdown-icon">
          <svg
            width="20"
            height="20"
            viewBox="0 0 38 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <g transform="translate(-110.711 -46.691)">
              <path d="M112.683 62.048c.765.357 3.22-.06 4.674.107 1.595.185 2.497 1.15 2.627 2.341.132 1.214 1.118 4.289 1.743 2.01.698-2.547 1.004-9.334 1.455-11.143.295-1.184 1.328-1.639 2.074-1.513.747.125 1.385.848 1.706 1.568s2.361 16.35 2.651 17.05 2.286-21.51 2.485-22.908c.189-1.337.514-2.872 2.095-2.869 1.47.004 2.128-.055 2.38 2.829.34 3.92 1.076 16.858 2.28 16.872.824.01 1.589-6.52 1.702-8.164.08-.97.748-1.85 1.651-1.913 1.006-.07 1.806.146 2.218 2.159.346 1.689.374 1.793.645 2.326.146.288.438.495.875.686 1.43.627 1.493-.213 2.384.51l.02 1.12c-.765.59-2.629.251-3.393-.226-.775-.484-1.983-.928-2.364-4.572-.233-2.23-.497 5.23-1.493 7.975-1.02 2.813-3.704 3.394-4.73-.055-.921-3.1-1.36-15.491-2.048-16.602-.715-1.155-2.133 21.101-2.704 22.817-.612 1.84-3.115 2.723-3.97-.078-.842-2.754-2.185-15.335-2.658-14.434-.47.894-.422 8.324-1.914 10.471-1.183 1.704-3.547 1.387-4.256-.863s-.312-2.692-1.33-3.252c-1.02-.56-4.904-.125-4.904-.125z"></path>
              <circle cx="112.552" cy="63.191" r="1.84"></circle>
              <circle cx="147.918" cy="62.526" r="1.84"></circle>
              <circle
                className="fill-background"
                cx="112.532"
                cy="63.216"
                r=".756"
              ></circle>
            </g>
          </svg>
        </span>
        <span className="trainwave-dropdown-arrow">{isOpen ? '▲' : '▼'}</span>
      </div>

      {isOpen && (
        <div className="trainwave-dropdown-menu" style={{ display: 'block' }}>
          {/* User Info Header */}
          <div className="trainwave-dropdown-header">
            {authService.isAuthenticated() && user ? (
              <div className="trainwave-user-info">
                {user?.picture && (
                  <img
                    src={user.picture}
                    alt="User"
                    width={40}
                    height={40}
                    className="trainwave-user-avatar"
                  />
                )}
                {!user?.picture && (
                  <div className="trainwave-user-avatar">
                    {user?.first_name?.[0] || user?.email?.[0] || 'U'}
                    {user?.last_name?.[0] || ''}
                  </div>
                )}
                <div className="trainwave-user-details">
                  <div className="trainwave-user-name">
                    {user?.first_name && user?.last_name
                      ? `${user.first_name} ${user.last_name}`
                      : user?.email || 'User'}
                  </div>
                  <div className="trainwave-user-email">{user?.email}</div>
                </div>
              </div>
            ) : (
              <div className="trainwave-login-section">
                <div className="trainwave-login-info">
                  <div className="trainwave-login-icon">🚀</div>
                  <div className="trainwave-login-text">
                    <div className="trainwave-login-title">
                      Welcome to Trainwave
                    </div>
                    <div className="trainwave-login-subtitle">
                      Sign in to access GPU workloads
                    </div>
                  </div>
                </div>
                <button
                  className="trainwave-login-button"
                  onClick={() => {
                    setIsOpen(false);
                    onLoginClick?.();
                  }}
                >
                  Sign In
                </button>
              </div>
            )}
          </div>

          {/* Launch Job Button */}
          {authService.isAuthenticated() && (
            <div className="trainwave-dropdown-section">
              {(() => {
                // Check if organization and project are configured
                const settings = authService.loadSettings();
                const hasOrgAndProject =
                  settings.organization_id && settings.project_id;
                const isButtonDisabled = isLaunchingJob || !hasOrgAndProject;

                return (
                  <>
                    <button
                      className="trainwave-launch-job-button"
                      disabled={isButtonDisabled}
                      onClick={async () => {
                        try {
                          setIsLaunchingJob(true);
                          console.log('Launching job...');

                          // Get current notebook and save it before launching
                          let notebookPath = null;
                          let defaultJobName = 'Untitled Job';

                          if (
                            notebookTracker &&
                            notebookTracker.currentWidget
                          ) {
                            const currentNotebook =
                              notebookTracker.currentWidget;
                            if (
                              currentNotebook.context &&
                              currentNotebook.context.path
                            ) {
                              notebookPath = currentNotebook.context.path;
                              console.log(
                                'Current notebook path:',
                                notebookPath
                              );

                              // Extract notebook name for default job name
                              const pathParts = notebookPath.split('/');
                              const fileName = pathParts[pathParts.length - 1];
                              const nameWithoutExtension = fileName.replace(
                                /\.(ipynb|py)$/,
                                ''
                              );
                              defaultJobName =
                                nameWithoutExtension || 'Untitled Job';

                              // Auto-save the notebook before launching
                              try {
                                await currentNotebook.context.save();
                                console.log('Notebook saved successfully');
                              } catch (saveError) {
                                console.error(
                                  'Failed to save notebook:',
                                  saveError
                                );
                                // Continue with launch even if save fails
                              }
                            }
                          }

                          // Show job name dialog
                          const jobName =
                            await showJobNameDialog(defaultJobName);
                          if (!jobName) {
                            // User cancelled
                            setIsLaunchingJob(false);
                            return;
                          }

                          // Get API key and settings from auth service
                          const apiKey = authService.getApiKey();
                          const settings = authService.loadSettings();

                          console.log(
                            JSON.stringify({
                              notebook_path: notebookPath,
                              project_id: settings.project_id,
                              gpu_type: settings.gpu_type,
                              gpu_count: settings.gpu_count,
                              job_name: jobName
                            })
                          );

                          const response = await requestAPI('launch-job', {
                            method: 'POST',
                            headers: {
                              'Content-Type': 'application/json',
                              'X-Api-Key': apiKey || ''
                            },
                            body: JSON.stringify({
                              notebook_path: notebookPath,
                              project_id: settings.project_id,
                              gpu_type: settings.gpu_type,
                              gpu_count: settings.gpu_count,
                              job_name: jobName
                            })
                          });
                          console.log('Launch job response:', response);
                          setIsOpen(false);
                        } catch (error) {
                          console.error('Failed to launch job:', error);
                          // You could show a user-friendly error message here
                        } finally {
                          setIsLaunchingJob(false);
                        }
                      }}
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke-width="1.5"
                        stroke="currentColor"
                        strokeWidth={1.5}
                        className="trainwave-icon trainwave-icon-white"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          d="M15.59 14.37a6 6 0 0 1-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 0 0 6.16-12.12A14.98 14.98 0 0 0 9.631 8.41m5.96 5.96a14.926 14.926 0 0 1-5.841 2.58m-.119-8.54a6 6 0 0 0-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 0 0-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 0 1-2.448-2.448 14.9 14.9 0 0 1 .06-.312m-2.24 2.39a4.493 4.493 0 0 0-1.757 4.306 4.493 4.493 0 0 0 4.306-1.758M16.5 9a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z"
                        />
                      </svg>
                      {isLaunchingJob ? 'Launching...' : 'Launch Job'}
                    </button>
                    {!hasOrgAndProject && (
                      <div className="trainwave-missing-config">
                        <HiMiniQuestionMarkCircle className="trainwave-icon trainwave-icon-orange" />
                        <div>
                          <div className="trainwave-missing-config-title">
                            Configure Organization & Project
                          </div>
                          <div className="trainwave-missing-config-message">
                            Please select an organization and project in
                            settings to launch jobs.
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                );
              })()}
            </div>
          )}

          {/* Active Jobs Section */}
          <div className="trainwave-dropdown-section">
            <div className="trainwave-section-title">Jobs</div>
            {(() => {
              // Check authentication first
              if (!authService.isAuthenticated()) {
                return (
                  <div className="trainwave-no-jobs">
                    <div className="trainwave-missing-config">
                      <HiMiniQuestionMarkCircle className="trainwave-icon-lg trainwave-icon-red" />
                      <div>
                        <div className="trainwave-missing-config-title">
                          Login Required
                        </div>
                        <div className="trainwave-missing-config-message">
                          Please log in to view your jobs.
                        </div>
                      </div>
                    </div>
                  </div>
                );
              }

              // Check organization and project configuration
              const settings = authService.loadSettings();
              const hasOrgAndProject =
                settings.organization_id && settings.project_id;

              if (!hasOrgAndProject) {
                return (
                  <div className="trainwave-no-jobs">
                    <div className="trainwave-missing-config">
                      <HiMiniQuestionMarkCircle className="trainwave-icon-lg trainwave-icon-red" />
                      <div>
                        <div className="trainwave-missing-config-title">
                          Select Organization & Project
                        </div>
                        <div className="trainwave-missing-config-message">
                          Please configure your organization and project in
                          settings to view jobs.
                        </div>
                      </div>
                    </div>
                  </div>
                );
              }

              if (isLoading && isInitialLoad) {
                return <div className="trainwave-loading">Loading jobs...</div>;
              }

              if (jobs.length === 0 && !isInitialLoad) {
                return <div className="trainwave-no-jobs">No active jobs</div>;
              }

              return (
                <div className="trainwave-jobs-list">
                  {jobs.slice(0, 5).map(job => (
                    <JobItem key={job.id} job={job} />
                  ))}
                  {jobs.length > 5 && (
                    <div className="trainwave-jobs-more">
                      <a
                        href="https://trainwave.ai/jobs"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <span className="trainwave-jobs-more-text">
                          View all jobs
                        </span>
                      </a>
                    </div>
                  )}
                </div>
              );
            })()}
          </div>

          {/* Actions Section */}
          <div className="trainwave-dropdown-section">
            <div className="trainwave-dropdown-actions">
              <button
                className="trainwave-dropdown-button"
                onClick={() => {
                  onSettingsClick();
                  setIsOpen(false);
                }}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  className="trainwave-icon trainwave-icon-gray"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
                  />
                </svg>
                Settings
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
