import React from 'react';
import { TrainwaveOrganization } from './api-client';
import { AuthService } from './auth';

interface OrganizationSelectorProps {
  authService: AuthService;
  onOrganizationSelected?: (organizationId: string) => void;
  onClose?: () => void;
}

interface OrganizationSelectorState {
  organizations: TrainwaveOrganization[];
  selectedOrganizationId: string;
  loading: boolean;
  error: string | null;
}

export class OrganizationSelector extends React.Component<
  OrganizationSelectorProps,
  OrganizationSelectorState
> {
  constructor(props: OrganizationSelectorProps) {
    super(props);
    this.state = {
      organizations: [],
      selectedOrganizationId: '',
      loading: true,
      error: null
    };
  }

  componentDidMount() {
    this.loadOrganizations();
  }

  private loadOrganizations = async () => {
    this.setState({ loading: true, error: null });

    try {
      const apiClient = this.props.authService.getApiClient();
      if (!apiClient) {
        throw new Error('No API client available');
      }

      const organizations = await apiClient.listOrganizations();
      this.setState({ organizations });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to load organizations';
      this.setState({ error: errorMessage });
      console.error('Failed to load organizations:', error);
    } finally {
      this.setState({ loading: false });
    }
  };

  private handleOrganizationSelect = (organizationId: string) => {
    this.setState({ selectedOrganizationId: organizationId });
  };

  private handleContinue = async () => {
    if (!this.state.selectedOrganizationId) {
      this.setState({ error: 'Please select an organization' });
      return;
    }

    try {
      this.setState({ loading: true, error: null });

      // Find the selected organization to get both RID and UUID
      const selectedOrg = this.state.organizations.find(
        org => org.rid === this.state.selectedOrganizationId
      );
      if (!selectedOrg) {
        throw new Error('Selected organization not found');
      }

      // Save the selected organization (both ID and RID)
      await this.props.authService.saveSettings({
        organization_id: selectedOrg.id, // UUID for API calls
        organization_rid: selectedOrg.rid // RID for display
      });

      // Get API client to work with projects
      const apiClient = this.props.authService.getApiClient();
      if (!apiClient) {
        throw new Error('No API client available');
      }

      // List all projects in the organization
      const projects = await apiClient.listProjects(
        this.state.selectedOrganizationId
      );

      // Look for existing "JupyterLab" project
      let jupyterLabProject = projects.find(
        project => project.name === 'JupyterLab'
      );

      if (!jupyterLabProject) {
        // Create new "JupyterLab" project (using UUID for API)
        console.log('Creating new JupyterLab project...');
        jupyterLabProject = await apiClient.createProject(
          'JupyterLab',
          selectedOrg.id // Use UUID instead of RID
        );
        console.log('JupyterLab project created:', jupyterLabProject);
      } else {
        console.log('Found existing JupyterLab project:', jupyterLabProject);
      }

      // Set the JupyterLab project as the selected project
      await this.props.authService.saveSettings({
        organization_id: selectedOrg.id,
        organization_rid: selectedOrg.rid,
        project_id: jupyterLabProject.id, // Use UUID for API calls
        project_rid: jupyterLabProject.rid // Use RID for display
      });

      // Notify parent component
      this.props.onOrganizationSelected?.(this.state.selectedOrganizationId);
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Failed to setup organization and project';
      this.setState({ error: errorMessage, loading: false });
      console.error('Failed to setup organization and project:', error);
    }
  };

  render(): React.ReactElement {
    const { organizations, selectedOrganizationId, loading, error } =
      this.state;

    return (
      <div className="trainwave-organization-selector">
        <div className="trainwave-organization-header">
          <h3>Select Organization</h3>
          <p>Choose which organization you want to use with Trainwave</p>
        </div>

        {error && (
          <div className="trainwave-organization-error">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="trainwave-organization-content">
          {loading ? (
            <div className="trainwave-organization-loading">
              <div className="trainwave-loading-spinner"></div>
              <p>Loading organizations...</p>
            </div>
          ) : organizations.length === 0 ? (
            <div className="trainwave-organization-empty">
              <p>
                No organizations found. Please create or join an organization by
                visiting the{' '}
                <a
                  href="https://trainwave.ai/jobs"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Trainwave website
                </a>
                .
              </p>
            </div>
          ) : (
            <div className="trainwave-organization-list">
              {organizations.map(org => (
                <div
                  key={org.id}
                  className={`trainwave-organization-item ${
                    selectedOrganizationId === org.rid ? 'selected' : ''
                  }`}
                  onClick={() => this.handleOrganizationSelect(org.rid)}
                >
                  <div className="trainwave-organization-info">
                    <div className="trainwave-organization-name">
                      {org.name}
                    </div>
                    <div className="trainwave-organization-balance">
                      Credit Balance: $
                      {(org.computed_credit_balance / 100).toFixed(2)}
                    </div>
                  </div>
                  <div className="trainwave-organization-radio">
                    <input
                      type="radio"
                      name="organization"
                      value={org.rid}
                      checked={selectedOrganizationId === org.rid}
                      onChange={() => this.handleOrganizationSelect(org.rid)}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="trainwave-organization-footer">
          <button
            className="trainwave-organization-button trainwave-organization-button-primary"
            onClick={this.handleContinue}
            disabled={loading || !selectedOrganizationId}
          >
            {loading ? 'Setting up...' : 'Continue'}
          </button>
          {this.props.onClose && (
            <button
              className="trainwave-organization-button trainwave-organization-button-secondary"
              onClick={this.props.onClose}
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    );
  }
}
