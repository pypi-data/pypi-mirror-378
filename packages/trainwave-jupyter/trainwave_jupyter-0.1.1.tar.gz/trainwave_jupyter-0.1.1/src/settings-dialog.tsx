import React from 'react';
import { Dialog } from '@jupyterlab/apputils';
import { AuthService } from './auth';
import { TrainwaveProject, TrainwaveOrganization } from './api-client';

interface GpuOffer {
  id: string;
  offer: number;
  cpus: number;
  memory_mb: number;
  gpus: number;
  gpu_type: string;
  gpu_memory_mb: number;
  compliance_soc2: boolean;
  tflops: number | null;
  grade: string | null;
}

interface GpuOption {
  gpu_type: string;
  min_price: number;
  display_name: string;
}

interface SettingsDialogProps {
  authService: AuthService;
  onClose: () => void;
}

interface SettingsState {
  apiEndpoint: string;
  pollingTimeout: number;
  pollingInterval: number;
  organizationId: string;
  projectId: string;
  gpuType: string;
  gpuCount: number;
  gpuOptions: GpuOption[];
  loadingGpuOptions: boolean;
  organizationOptions: TrainwaveOrganization[];
  loadingOrganizationOptions: boolean;
  projectOptions: TrainwaveProject[];
  loadingProjectOptions: boolean;
}

export class SettingsDialog extends React.Component<
  SettingsDialogProps,
  SettingsState
> {
  constructor(props: SettingsDialogProps) {
    super(props);
    this.state = {
      apiEndpoint: 'https://backend.trainwave.ai',
      pollingTimeout: 300000, // 5 minutes
      pollingInterval: 2000, // 2 seconds
      organizationId: '',
      projectId: '',
      gpuType: 'CPU',
      gpuCount: 1,
      gpuOptions: [],
      loadingGpuOptions: false,
      organizationOptions: [],
      loadingOrganizationOptions: false,
      projectOptions: [],
      loadingProjectOptions: false
    };
  }

  componentDidMount() {
    this.loadSettings();
    this.loadGpuOptions();
    this.loadOrganizationOptions();
  }

  private loadSettings = () => {
    // Load settings from the auth service or settings registry
    const config = this.props.authService.getConfig();
    const savedSettings = this.props.authService.loadSettings();

    this.setState({
      apiEndpoint: config.endpoint || 'https://backend.trainwave.ai',
      pollingTimeout: config.polling_timeout || 300000,
      pollingInterval: config.polling_interval || 2000,
      organizationId: savedSettings.organization_rid, // Use RID for display
      projectId: savedSettings.project_rid, // Use RID for display
      gpuType: savedSettings.gpu_type,
      gpuCount: savedSettings.gpu_count
    });

    // Load projects for the current organization if one is selected
    // Use organization_rid for filtering projects (as the API expects RID for filtering)
    if (savedSettings.organization_rid) {
      this.loadProjectOptions(savedSettings.organization_rid);
    }
  };

  private loadGpuOptions = async () => {
    this.setState({ loadingGpuOptions: true });

    try {
      const apiClient = this.props.authService.getApiClient();
      if (!apiClient) {
        console.warn('No API client available for fetching GPU options');
        return;
      }

      // Fetch offers from the API using the API client
      const offers: GpuOffer[] = await apiClient.listOffers();

      // Process offers to get unique GPU types with minimum prices
      const gpuMap = new Map<
        string,
        { minPrice: number; displayName: string }
      >();

      offers.forEach(offer => {
        if (offer.gpu_type) {
          const existing = gpuMap.get(offer.gpu_type);
          if (!existing || offer.offer < existing.minPrice) {
            // Create a clean display name
            const displayName = offer.gpu_type
              .replace('NVIDIA-', '')
              .replace('AMD-', '')
              .replace('-', ' ')
              .replace(/(\d+)GB/, '$1GB');

            gpuMap.set(offer.gpu_type, {
              minPrice: offer.offer,
              displayName
            });
          }
        }
      });

      // Convert to array and sort by price
      const gpuOptions: GpuOption[] = Array.from(gpuMap.entries())
        .map(([gpu_type, data]) => ({
          gpu_type,
          min_price: data.minPrice,
          display_name: data.displayName
        }))
        .sort((a, b) => a.min_price - b.min_price);

      this.setState({ gpuOptions });
    } catch (error) {
      console.error('Failed to load GPU options:', error);
      // Fallback to default options if API fails
      this.setState({
        gpuOptions: [
          {
            gpu_type: 'NVIDIA-A100-80GB',
            min_price: 2.3,
            display_name: 'A100 80GB'
          },
          {
            gpu_type: 'NVIDIA-H100-80GB',
            min_price: 3.1,
            display_name: 'H100 80GB'
          },
          {
            gpu_type: 'NVIDIA-V100-16GB',
            min_price: 0.5,
            display_name: 'V100 16GB'
          },
          {
            gpu_type: 'NVIDIA-RTX-4090-24GB',
            min_price: 1.1,
            display_name: 'RTX 4090 24GB'
          },
          {
            gpu_type: 'NVIDIA-RTX-3090-24GB',
            min_price: 0.9,
            display_name: 'RTX 3090 24GB'
          }
        ]
      });
    } finally {
      this.setState({ loadingGpuOptions: false });
    }
  };

  private loadOrganizationOptions = async () => {
    this.setState({ loadingOrganizationOptions: true });

    try {
      const apiClient = this.props.authService.getApiClient();
      if (!apiClient) {
        console.warn(
          'No API client available for fetching organization options'
        );
        return;
      }

      // Fetch organizations from the API using the API client
      const organizations: TrainwaveOrganization[] =
        await apiClient.listOrganizations();

      this.setState({ organizationOptions: organizations });
    } catch (error) {
      console.error('Failed to load organization options:', error);
      // Fallback to empty array if API fails
      this.setState({
        organizationOptions: []
      });
    } finally {
      this.setState({ loadingOrganizationOptions: false });
    }
  };

  private loadProjectOptions = async (organizationId?: string) => {
    this.setState({ loadingProjectOptions: true });

    try {
      const apiClient = this.props.authService.getApiClient();
      if (!apiClient) {
        console.warn('No API client available for fetching project options');
        return;
      }

      // Fetch projects from the API using the API client with organization filter
      const projects: TrainwaveProject[] =
        await apiClient.listProjects(organizationId);

      this.setState({ projectOptions: projects });
    } catch (error) {
      console.error('Failed to load project options:', error);
      // Fallback to empty array if API fails
      this.setState({
        projectOptions: []
      });
    } finally {
      this.setState({ loadingProjectOptions: false });
    }
  };

  private saveSettings = async (settings: {
    organization_id?: string;
    organization_rid?: string;
    project_id?: string;
    project_rid?: string;
    gpu_type?: string;
    gpu_count?: number;
  }) => {
    try {
      await this.props.authService.saveSettings(settings);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  };

  private handleLogout = async () => {
    try {
      await this.props.authService.logout();
      // Trigger UI update to reflect logout state
      if ((window as any).updateTrainwaveToolbars) {
        (window as any).updateTrainwaveToolbars();
      }
      // Refresh dropdown to show logged out state
      if ((window as any).refreshTrainwaveDropdown) {
        (window as any).refreshTrainwaveDropdown();
      }
      this.props.onClose();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  render() {
    const { authService } = this.props;
    const {
      apiEndpoint,
      pollingTimeout,
      pollingInterval,
      organizationId,
      projectId,
      gpuType,
      gpuCount,
      gpuOptions,
      loadingGpuOptions,
      organizationOptions,
      loadingOrganizationOptions,
      projectOptions,
      loadingProjectOptions
    } = this.state;
    const user = authService.getUser();

    return (
      <div className="trainwave-settings-dialog">
        {/* <div className="trainwave-settings-header">
          <h3>Trainwave Settings</h3>
          <p>Configure your Trainwave integration</p>
        </div> */}

        {/* Authentication Section */}
        <div className="trainwave-settings-section">
          <h4>Authentication</h4>
          {user ? (
            <div className="trainwave-auth-status">
              <div className="trainwave-user-info">
                <div className="trainwave-user-avatar">
                  {user.first_name?.[0] || user.email?.[0] || 'U'}
                </div>
                <div className="trainwave-user-details">
                  <div className="trainwave-user-name">
                    {user.first_name && user.last_name
                      ? `${user.first_name} ${user.last_name}`
                      : user.email}
                  </div>
                  <div className="trainwave-user-email">{user.email}</div>
                </div>
              </div>
              <div className="trainwave-auth-actions">
                <button
                  className="trainwave-settings-button trainwave-logout-button"
                  onClick={this.handleLogout}
                >
                  Logout
                </button>
              </div>
            </div>
          ) : (
            <div className="trainwave-not-authenticated">
              <p>Not authenticated</p>
              <button
                className="trainwave-settings-button trainwave-primary-button"
                onClick={() => {
                  this.props.onClose();
                  // Trigger authentication
                  authService.authenticate();
                }}
              >
                Authenticate
              </button>
            </div>
          )}
        </div>

        <div className="trainwave-settings-section">
          <h4>Organization & Jobs</h4>
          <div className="trainwave-settings-field">
            <label htmlFor="organization-id">Organization</label>
            <select
              id="organization-id"
              value={organizationId}
              onChange={e => {
                const newOrganizationRid = e.target.value;
                this.setState({
                  organizationId: newOrganizationRid,
                  projectId: '' // Clear project selection when organization changes
                });

                // Find the organization to get both ID and RID
                const selectedOrg = this.state.organizationOptions.find(
                  org => org.rid === newOrganizationRid
                );

                this.saveSettings({
                  organization_id: selectedOrg?.id || '',
                  organization_rid: newOrganizationRid,
                  project_id: '', // Clear project setting
                  project_rid: '' // Clear project RID setting
                });

                // Reload projects for the new organization
                if (newOrganizationRid) {
                  this.loadProjectOptions(newOrganizationRid);
                } else {
                  this.setState({ projectOptions: [] });
                }
              }}
              disabled={loadingOrganizationOptions}
            >
              {loadingOrganizationOptions ? (
                <option value="">Loading organizations...</option>
              ) : organizationOptions.length === 0 ? (
                <option value="">No organizations available</option>
              ) : (
                <>
                  <option value="">Select an organization</option>
                  {organizationOptions.map(org => (
                    <option key={org.id} value={org.rid}>
                      {org.name} ($
                      {(org.computed_credit_balance / 100).toFixed(2)})
                    </option>
                  ))}
                </>
              )}
            </select>
            {loadingOrganizationOptions && (
              <div className="trainwave-loading-text">
                Loading organizations from API...
              </div>
            )}
          </div>
          <div className="trainwave-settings-field">
            <label htmlFor="project-id">Project</label>
            <select
              id="project-id"
              value={projectId}
              onChange={e => {
                const newProjectRid = e.target.value;
                this.setState({ projectId: newProjectRid });

                // Find the project to get both ID and RID
                const selectedProject = this.state.projectOptions.find(
                  project => project.rid === newProjectRid
                );

                this.saveSettings({
                  project_id: selectedProject?.id || '', // Use UUID for API calls
                  project_rid: newProjectRid // Use RID for display
                });
              }}
              disabled={!organizationId || loadingProjectOptions}
            >
              {!organizationId ? (
                <option value="">Select an organization first</option>
              ) : loadingProjectOptions ? (
                <option value="">Loading projects...</option>
              ) : projectOptions.length === 0 ? (
                <option value="">
                  No projects available for this organization
                </option>
              ) : (
                <>
                  <option value="">Select a project</option>
                  {projectOptions.map(project => (
                    <option key={project.id} value={project.rid}>
                      {project.name} ({project.total_job_count} jobs)
                    </option>
                  ))}
                </>
              )}
            </select>
            {loadingProjectOptions && (
              <div className="trainwave-loading-text">
                Loading projects from API...
              </div>
            )}
            {!organizationId && (
              <div className="trainwave-loading-text">
                Please select an organization to view available projects
              </div>
            )}
          </div>
          <div className="trainwave-settings-field">
            <label htmlFor="gpu-type">GPU Type</label>
            <select
              id="gpu-type"
              value={gpuType}
              onChange={e => {
                const newGpuType = e.target.value;
                this.setState({ gpuType: newGpuType });
                this.saveSettings({ gpu_type: newGpuType });
              }}
              disabled={loadingGpuOptions}
            >
              {loadingGpuOptions ? (
                <option value="">Loading GPU options...</option>
              ) : (
                <>
                  <option value="CPU">CPU Only</option>
                  {gpuOptions.map(option => (
                    <option key={option.gpu_type} value={option.gpu_type}>
                      {option.display_name} - ${option.min_price.toFixed(2)}/hr
                    </option>
                  ))}
                </>
              )}
            </select>
            {loadingGpuOptions && (
              <div className="trainwave-loading-text">
                Loading GPU options from API...
              </div>
            )}
          </div>
          <div className="trainwave-settings-field">
            <label htmlFor="gpu-count">Number of CPUs/GPUs</label>
            <input
              id="gpu-count"
              type="number"
              min="1"
              value={gpuCount}
              onChange={e => {
                const newGpuCount = parseInt(e.target.value) || 1;
                this.setState({ gpuCount: newGpuCount });
                this.saveSettings({ gpu_count: newGpuCount });
              }}
            />
          </div>
        </div>

        {/* API Configuration Section */}
        <div className="trainwave-settings-section">
          <h4>API</h4>
          <div className="trainwave-settings-field">
            <label htmlFor="api-endpoint">API Endpoint</label>
            <input
              id="api-endpoint"
              type="text"
              value={apiEndpoint}
              onChange={e => this.setState({ apiEndpoint: e.target.value })}
              placeholder="https://backend.trainwave.ai"
            />
          </div>
          <div className="trainwave-settings-field">
            <label htmlFor="polling-timeout">Polling Timeout (ms)</label>
            <input
              id="polling-timeout"
              type="number"
              value={pollingTimeout}
              onChange={e =>
                this.setState({
                  pollingTimeout: parseInt(e.target.value) || 300000
                })
              }
              min="10000"
              max="600000"
            />
          </div>
          <div className="trainwave-settings-field">
            <label htmlFor="polling-interval">Polling Interval (ms)</label>
            <input
              id="polling-interval"
              type="number"
              value={pollingInterval}
              onChange={e =>
                this.setState({
                  pollingInterval: parseInt(e.target.value) || 2000
                })
              }
              min="1000"
              max="10000"
            />
          </div>
        </div>
      </div>
    );
  }
}

export function showSettingsDialog(authService: AuthService): Promise<void> {
  return new Promise<void>(resolve => {
    let resolved = false;

    const dialog = new Dialog({
      title: 'Trainwave Settings',
      body: React.createElement(SettingsDialog, {
        authService,
        onClose: () => {
          if (!resolved) {
            resolved = true;
            dialog.resolve();
            resolve();
          }
        }
      }),
      buttons: [Dialog.cancelButton({ label: 'Close' })],
      focusNodeSelector: '.trainwave-primary-button'
    });

    dialog.launch().then(() => {
      if (!resolved) {
        resolved = true;
        resolve();
      }
    });
  });
}
