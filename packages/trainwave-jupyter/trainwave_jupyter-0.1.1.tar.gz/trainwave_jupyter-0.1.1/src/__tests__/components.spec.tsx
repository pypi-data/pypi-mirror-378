/**
 * Tests for React components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

import { AuthDialog } from '../auth-dialog';
import { SettingsDialog } from '../settings-dialog';
import { TrainwaveDropdown } from '../dropdown';
import { OrganizationSelector } from '../organization-selector';
import { JobNameDialog } from '../job-name-dialog';
import { AuthService } from '../auth';
import {
  TrainwaveUser,
  TrainwaveProject,
  TrainwaveOrganization,
  Job,
  JobStatus
} from '../api-client';

// Mock the JupyterLab modules
jest.mock('@jupyterlab/apputils', () => ({
  Dialog: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="dialog">{children}</div>
  )
}));

jest.mock('@jupyterlab/notebook', () => ({
  INotebookTracker: {}
}));

// Mock the requestAPI function
jest.mock('../handler', () => ({
  requestAPI: jest.fn()
}));

describe('AuthDialog', () => {
  let mockAuthService: jest.Mocked<AuthService>;
  let mockOnAuthSuccess: jest.Mock;
  let mockOnAuthError: jest.Mock;

  beforeEach(() => {
    mockOnAuthSuccess = jest.fn();
    mockOnAuthError = jest.fn();

    mockAuthService = {
      isAuthenticated: jest.fn(),
      authenticate: jest.fn(),
      logout: jest.fn(),
      getUser: jest.fn(),
      loadSettings: jest.fn().mockReturnValue({
        organization_id: 'test-org',
        organization_rid: 'test-org-rid',
        project_id: 'test-project',
        project_rid: 'test-project-rid',
        gpu_type: 'CPU',
        gpu_count: 1
      })
    } as any;
  });

  it('should render login form when not authenticated', () => {
    mockAuthService.isAuthenticated.mockReturnValue(false);

    render(
      <AuthDialog
        authService={mockAuthService}
        onAuthSuccess={mockOnAuthSuccess}
        onAuthError={mockOnAuthError}
      />
    );

    expect(screen.getByText('Trainwave Authentication')).toBeInTheDocument();
    expect(
      screen.getByText('Connect your Trainwave account to access GPU workloads')
    ).toBeInTheDocument();
    expect(screen.getByText('Authenticate with Trainwave')).toBeInTheDocument();
  });

  it('should render success state when authenticated', () => {
    mockAuthService.isAuthenticated.mockReturnValue(true);

    render(
      <AuthDialog
        authService={mockAuthService}
        onAuthSuccess={mockOnAuthSuccess}
        onAuthError={mockOnAuthError}
      />
    );

    expect(
      screen.getByText('You are authenticated with Trainwave')
    ).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  it('should handle authentication success', async () => {
    mockAuthService.isAuthenticated.mockReturnValue(false);
    mockAuthService.authenticate.mockResolvedValue(true);

    render(
      <AuthDialog
        authService={mockAuthService}
        onAuthSuccess={mockOnAuthSuccess}
        onAuthError={mockOnAuthError}
      />
    );

    const loginButton = screen.getByText('Authenticate with Trainwave');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(mockAuthService.authenticate).toHaveBeenCalled();
      expect(mockOnAuthSuccess).toHaveBeenCalled();
    });
  });

  it('should handle authentication error', async () => {
    mockAuthService.isAuthenticated.mockReturnValue(false);
    mockAuthService.authenticate.mockRejectedValue(
      new Error('Authentication failed')
    );

    render(
      <AuthDialog
        authService={mockAuthService}
        onAuthSuccess={mockOnAuthSuccess}
        onAuthError={mockOnAuthError}
      />
    );

    const loginButton = screen.getByText('Authenticate with Trainwave');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Authentication failed')).toBeInTheDocument();
      expect(mockOnAuthError).toHaveBeenCalledWith('Authentication failed');
    });
  });

  it('should handle logout', async () => {
    mockAuthService.isAuthenticated.mockReturnValue(true);
    mockAuthService.logout.mockResolvedValue();

    render(
      <AuthDialog
        authService={mockAuthService}
        onAuthSuccess={mockOnAuthSuccess}
        onAuthError={mockOnAuthError}
      />
    );

    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);

    await waitFor(() => {
      expect(mockAuthService.logout).toHaveBeenCalled();
      expect(mockOnAuthSuccess).toHaveBeenCalled();
    });
  });

  it('should show loading state during authentication', async () => {
    mockAuthService.isAuthenticated.mockReturnValue(false);
    mockAuthService.authenticate.mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    render(
      <AuthDialog
        authService={mockAuthService}
        onAuthSuccess={mockOnAuthSuccess}
        onAuthError={mockOnAuthError}
      />
    );

    const loginButton = screen.getByText('Authenticate with Trainwave');
    fireEvent.click(loginButton);

    expect(screen.getByText('Authenticating...')).toBeInTheDocument();
    expect(loginButton).toBeDisabled();
  });
});

describe('SettingsDialog', () => {
  let mockAuthService: jest.Mocked<AuthService>;
  let mockOnClose: jest.Mock;

  beforeEach(() => {
    mockOnClose = jest.fn();

    const mockApiClient = {
      listOffers: jest.fn().mockResolvedValue([]),
      listProjects: jest.fn().mockResolvedValue([])
    } as any;

    mockAuthService = {
      getConfig: jest.fn().mockReturnValue({
        endpoint: 'https://test.trainwave.ai',
        polling_timeout: 300,
        polling_interval: 2
      }),
      loadSettings: jest.fn().mockReturnValue({
        organization_id: 'test-org',
        organization_rid: 'test-org-rid',
        project_id: 'test-project',
        project_rid: 'test-project-rid',
        gpu_type: 'A100',
        gpu_count: 1
      }),
      saveSettings: jest.fn(),
      getUser: jest.fn().mockReturnValue({
        id: '1',
        email: 'test@example.com',
        first_name: 'Test'
      }),
      getApiClient: jest.fn().mockReturnValue(mockApiClient)
    } as any;
  });

  it('should render settings form', () => {
    render(
      <SettingsDialog authService={mockAuthService} onClose={mockOnClose} />
    );

    expect(screen.getByText('Authentication')).toBeInTheDocument();
    expect(
      screen.getByDisplayValue('https://test.trainwave.ai')
    ).toBeInTheDocument();
    expect(screen.getByDisplayValue('1')).toBeInTheDocument();
  });

  it('should load GPU options on mount', async () => {
    const mockOffers = [
      {
        id: '1',
        cpus: 4,
        memory_mb: 8192,
        gpus: 1,
        gpu_type: 'A100',
        gpu_memory_mb: 40960,
        compliance_soc2: true,
        offer: 1.5
      },
      {
        id: '2',
        cpus: 8,
        memory_mb: 16384,
        gpus: 2,
        gpu_type: 'V100',
        gpu_memory_mb: 32768,
        compliance_soc2: true,
        offer: 1.0
      }
    ];

    const mockApiClient = mockAuthService.getApiClient();
    (mockApiClient.listOffers as jest.Mock).mockResolvedValue(mockOffers);

    render(
      <SettingsDialog authService={mockAuthService} onClose={mockOnClose} />
    );

    await waitFor(() => {
      expect(mockApiClient.listOffers).toHaveBeenCalled();
    });
  });

  it('should load project options on mount', async () => {
    const mockProjects: TrainwaveProject[] = [
      {
        id: '1',
        rid: 'rid-1',
        name: 'Test Project',
        active_job_count: 2,
        total_job_count: 5,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-02T00:00:00Z',
        organization: 'org-1',
        users: ['user-1']
      }
    ];

    const mockApiClient = mockAuthService.getApiClient();
    (mockApiClient.listProjects as jest.Mock).mockResolvedValue(mockProjects);

    render(
      <SettingsDialog authService={mockAuthService} onClose={mockOnClose} />
    );

    await waitFor(() => {
      expect(mockApiClient.listProjects).toHaveBeenCalled();
    });
  });
});

describe('TrainwaveDropdown', () => {
  let mockAuthService: jest.Mocked<AuthService>;
  let mockNotebookTracker: any;
  let mockOnSettingsClick: jest.Mock;
  let mockOnLoginClick: jest.Mock;

  beforeEach(() => {
    mockOnSettingsClick = jest.fn();
    mockOnLoginClick = jest.fn();

    const mockApiClient = {
      listJobs: jest.fn().mockResolvedValue([])
    } as any;

    mockAuthService = {
      isAuthenticated: jest.fn(),
      getUser: jest.fn(),
      getApiClient: jest.fn().mockReturnValue(mockApiClient),
      loadSettings: jest.fn().mockReturnValue({
        organization_id: '',
        organization_rid: '',
        project_id: '',
        project_rid: '',
        gpu_type: 'CPU',
        gpu_count: 1
      })
    } as any;

    mockNotebookTracker = {
      currentWidget: null,
      forEach: jest.fn()
    };
  });

  it('should render login button when not authenticated', () => {
    mockAuthService.isAuthenticated.mockReturnValue(false);

    render(
      <TrainwaveDropdown
        authService={mockAuthService}
        notebookTracker={mockNotebookTracker}
        onSettingsClick={mockOnSettingsClick}
        onLoginClick={mockOnLoginClick}
      />
    );

    // Click the dropdown trigger to open the menu
    const dropdownTrigger = document.querySelector(
      '.trainwave-dropdown-trigger'
    );
    fireEvent.click(dropdownTrigger!);

    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  it('should render user info when authenticated', () => {
    const mockUser: TrainwaveUser = {
      id: '1',
      rid: 'rid-1',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User'
    };

    mockAuthService.isAuthenticated.mockReturnValue(true);
    mockAuthService.getUser.mockReturnValue(mockUser);

    render(
      <TrainwaveDropdown
        authService={mockAuthService}
        notebookTracker={mockNotebookTracker}
        onSettingsClick={mockOnSettingsClick}
        onLoginClick={mockOnLoginClick}
      />
    );

    // Click the dropdown trigger to open the menu
    const dropdownTrigger = document.querySelector(
      '.trainwave-dropdown-trigger'
    );
    fireEvent.click(dropdownTrigger!);

    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('should handle login click', () => {
    mockAuthService.isAuthenticated.mockReturnValue(false);

    render(
      <TrainwaveDropdown
        authService={mockAuthService}
        notebookTracker={mockNotebookTracker}
        onSettingsClick={mockOnSettingsClick}
        onLoginClick={mockOnLoginClick}
      />
    );

    // Click the dropdown trigger to open the menu
    const dropdownTrigger = document.querySelector(
      '.trainwave-dropdown-trigger'
    );
    fireEvent.click(dropdownTrigger!);

    const loginButton = screen.getByText('Sign In');
    fireEvent.click(loginButton);

    expect(mockOnLoginClick).toHaveBeenCalled();
  });

  it('should handle settings click', () => {
    const mockUser: TrainwaveUser = {
      id: '1',
      rid: 'rid-1',
      email: 'test@example.com'
    };

    mockAuthService.isAuthenticated.mockReturnValue(true);
    mockAuthService.getUser.mockReturnValue(mockUser);

    render(
      <TrainwaveDropdown
        authService={mockAuthService}
        notebookTracker={mockNotebookTracker}
        onSettingsClick={mockOnSettingsClick}
        onLoginClick={mockOnLoginClick}
      />
    );

    // Click the dropdown trigger to open the menu
    const dropdownTrigger = document.querySelector(
      '.trainwave-dropdown-trigger'
    );
    fireEvent.click(dropdownTrigger!);

    const settingsButton = screen.getByText('Settings');
    fireEvent.click(settingsButton);

    expect(mockOnSettingsClick).toHaveBeenCalled();
  });

  it('should load and display jobs when authenticated', async () => {
    const mockUser: TrainwaveUser = {
      id: '1',
      rid: 'rid-1',
      email: 'test@example.com'
    };

    const mockJobs: Job[] = [
      {
        id: '1',
        rid: 'rid-1',
        state: JobStatus.RUNNING,
        s3_url: 's3://bucket/key',
        project: {} as TrainwaveProject,
        cloud_offer: {
          cpus: 4,
          memory_mb: 8192,
          compliance_soc2: true,
          gpu_type: 'A100',
          gpu_memory_mb: 40960,
          gpus: 1
        },
        cost_per_hour: 2.5,
        config: {
          id: '1',
          rid: 'rid-1',
          name: 'test-config',
          expires_at: Date.now() + 3600000,
          cpus: 4,
          gpus: 1,
          gpu_type: 'A100'
        },
        created_at: '2023-01-01T00:00:00Z',
        total_cost: 5.0,
        upload_url: 'https://upload.url'
      }
    ];

    mockAuthService.isAuthenticated.mockReturnValue(true);
    mockAuthService.getUser.mockReturnValue(mockUser);

    const mockApiClient = mockAuthService.getApiClient();
    (mockApiClient.listJobs as jest.Mock).mockResolvedValue(mockJobs);

    render(
      <TrainwaveDropdown
        authService={mockAuthService}
        notebookTracker={mockNotebookTracker}
        onSettingsClick={mockOnSettingsClick}
        onLoginClick={mockOnLoginClick}
      />
    );

    await waitFor(() => {
      expect(mockApiClient.listJobs).toHaveBeenCalledWith('', '');
    });
  });

  it('should show login required message when not authenticated', () => {
    mockAuthService.isAuthenticated.mockReturnValue(false);

    render(
      <TrainwaveDropdown
        authService={mockAuthService}
        notebookTracker={mockNotebookTracker}
        onSettingsClick={mockOnSettingsClick}
        onLoginClick={mockOnLoginClick}
      />
    );

    // Click the dropdown trigger to open the menu
    fireEvent.click(document.querySelector('.trainwave-dropdown-trigger')!);

    expect(screen.getByText('Login Required')).toBeInTheDocument();
    expect(
      screen.getByText('Please log in to view your jobs.')
    ).toBeInTheDocument();
  });

  it('should show organization/project message when authenticated but not configured', () => {
    mockAuthService.isAuthenticated.mockReturnValue(true);
    mockAuthService.loadSettings.mockReturnValue({
      organization_id: '',
      organization_rid: '',
      project_id: '',
      project_rid: '',
      gpu_type: 'CPU',
      gpu_count: 1
    });

    render(
      <TrainwaveDropdown
        authService={mockAuthService}
        notebookTracker={mockNotebookTracker}
        onSettingsClick={mockOnSettingsClick}
        onLoginClick={mockOnLoginClick}
      />
    );

    // Click the dropdown trigger to open the menu
    fireEvent.click(document.querySelector('.trainwave-dropdown-trigger')!);

    expect(
      screen.getByText('Select Organization & Project')
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        'Please configure your organization and project in settings to view jobs.'
      )
    ).toBeInTheDocument();
  });
});

describe('OrganizationSelector', () => {
  let mockAuthService: jest.Mocked<AuthService>;
  let mockOnOrganizationSelected: jest.Mock;
  let mockOnClose: jest.Mock;

  beforeEach(() => {
    mockOnOrganizationSelected = jest.fn();
    mockOnClose = jest.fn();

    const mockApiClient = {
      listOrganizations: jest.fn().mockResolvedValue([]),
      listProjects: jest.fn().mockResolvedValue([]),
      createProject: jest.fn().mockResolvedValue({
        id: '1',
        rid: 'proj-1',
        name: 'JupyterLab',
        active_job_count: 0,
        total_job_count: 0,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        organization: 'org-1',
        users: ['user-1']
      })
    } as any;

    mockAuthService = {
      getApiClient: jest.fn().mockReturnValue(mockApiClient),
      saveSettings: jest.fn().mockResolvedValue(undefined)
    } as any;
  });

  it('should render organization selector', () => {
    render(
      <OrganizationSelector
        authService={mockAuthService}
        onOrganizationSelected={mockOnOrganizationSelected}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Select Organization')).toBeInTheDocument();
    expect(
      screen.getByText(
        'Choose which organization you want to use with Trainwave'
      )
    ).toBeInTheDocument();
  });

  it('should load organizations on mount', async () => {
    const mockOrganizations: TrainwaveOrganization[] = [
      {
        id: '1',
        rid: 'org-1',
        name: 'Test Organization',
        computed_credit_balance: 100000
      },
      {
        id: '2',
        rid: 'org-2',
        name: 'Another Organization',
        computed_credit_balance: 50000
      }
    ];

    const mockApiClient = mockAuthService.getApiClient();
    (mockApiClient.listOrganizations as jest.Mock).mockResolvedValue(
      mockOrganizations
    );

    render(
      <OrganizationSelector
        authService={mockAuthService}
        onOrganizationSelected={mockOnOrganizationSelected}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(mockApiClient.listOrganizations).toHaveBeenCalled();
      expect(screen.getByText('Test Organization')).toBeInTheDocument();
      expect(screen.getByText('Another Organization')).toBeInTheDocument();
    });
  });

  it('should handle organization selection', async () => {
    const mockOrganizations: TrainwaveOrganization[] = [
      {
        id: '550e8400-e29b-41d4-a716-446655440000', // UUID format
        rid: 'org-1',
        name: 'Test Organization',
        computed_credit_balance: 100000
      }
    ];

    const mockApiClient = mockAuthService.getApiClient();
    (mockApiClient.listOrganizations as jest.Mock).mockResolvedValue(
      mockOrganizations
    );
    // Mock empty projects list (no existing JupyterLab project)
    (mockApiClient.listProjects as jest.Mock).mockResolvedValue([]);
    // Mock project creation
    (mockApiClient.createProject as jest.Mock).mockResolvedValue({
      id: '1',
      rid: 'proj-1',
      name: 'JupyterLab',
      active_job_count: 0,
      total_job_count: 0,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z',
      organization: 'org-1',
      users: ['user-1']
    });
    mockAuthService.saveSettings.mockResolvedValue(undefined);

    render(
      <OrganizationSelector
        authService={mockAuthService}
        onOrganizationSelected={mockOnOrganizationSelected}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Test Organization')).toBeInTheDocument();
    });

    const organizationItem = screen
      .getByText('Test Organization')
      .closest('.trainwave-organization-item');
    fireEvent.click(organizationItem!);

    const continueButton = screen.getByText('Continue');
    fireEvent.click(continueButton);

    await waitFor(() => {
      expect(mockAuthService.saveSettings).toHaveBeenCalledWith({
        organization_id: '550e8400-e29b-41d4-a716-446655440000',
        organization_rid: 'org-1',
        project_id: '1', // UUID from mock project
        project_rid: 'proj-1' // RID from mock project
      });
      expect(mockOnOrganizationSelected).toHaveBeenCalledWith('org-1');
    });
  });

  it('should show loading state', () => {
    const mockApiClient = mockAuthService.getApiClient();
    (mockApiClient.listOrganizations as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    render(
      <OrganizationSelector
        authService={mockAuthService}
        onOrganizationSelected={mockOnOrganizationSelected}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Loading organizations...')).toBeInTheDocument();
  });

  it('should show error state', async () => {
    const mockApiClient = mockAuthService.getApiClient();
    (mockApiClient.listOrganizations as jest.Mock).mockRejectedValue(
      new Error('Failed to load organizations')
    );

    render(
      <OrganizationSelector
        authService={mockAuthService}
        onOrganizationSelected={mockOnOrganizationSelected}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(
        screen.getByText('Failed to load organizations')
      ).toBeInTheDocument();
    });
  });

  it('should show empty state when no organizations', async () => {
    const mockApiClient = mockAuthService.getApiClient();
    (mockApiClient.listOrganizations as jest.Mock).mockResolvedValue([]);

    render(
      <OrganizationSelector
        authService={mockAuthService}
        onOrganizationSelected={mockOnOrganizationSelected}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(
        screen.getByText((content, element) => {
          return (
            element?.tagName === 'P' &&
            element?.textContent ===
              'No organizations found. Please create or join an organization by visiting the Trainwave website.'
          );
        })
      ).toBeInTheDocument();
    });
  });
});

describe('JobNameDialog', () => {
  let mockOnConfirm: jest.Mock;
  let mockOnCancel: jest.Mock;

  beforeEach(() => {
    mockOnConfirm = jest.fn();
    mockOnCancel = jest.fn();
  });

  it('should render job name dialog with default name', () => {
    render(
      <JobNameDialog
        defaultName="My Notebook"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText('Job Name')).toBeInTheDocument();
    expect(screen.getByDisplayValue('My Notebook')).toBeInTheDocument();
    expect(screen.getByText('Launch Job')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('should update job name when user types', () => {
    render(
      <JobNameDialog
        defaultName="My Notebook"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const input = screen.getByDisplayValue('My Notebook');
    fireEvent.change(input, { target: { value: 'Custom Job Name' } });

    expect(screen.getByDisplayValue('Custom Job Name')).toBeInTheDocument();
  });

  it('should call onConfirm with job name when Launch Job is clicked', () => {
    render(
      <JobNameDialog
        defaultName="My Notebook"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const launchButton = screen.getByText('Launch Job');
    fireEvent.click(launchButton);

    expect(mockOnConfirm).toHaveBeenCalledWith('My Notebook');
  });

  it('should call onCancel when Cancel is clicked', () => {
    render(
      <JobNameDialog
        defaultName="My Notebook"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('should disable Launch Job button when job name is empty', () => {
    render(
      <JobNameDialog
        defaultName=""
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const launchButton = screen.getByText('Launch Job');
    expect(launchButton).toBeDisabled();
  });

  it('should enable Launch Job button when job name has content', () => {
    render(
      <JobNameDialog
        defaultName="My Job"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const launchButton = screen.getByText('Launch Job');
    expect(launchButton).not.toBeDisabled();
  });

  it('should call onConfirm when Enter key is pressed', () => {
    render(
      <JobNameDialog
        defaultName="My Notebook"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const input = screen.getByDisplayValue('My Notebook');
    fireEvent.keyDown(input, { key: 'Enter' });

    expect(mockOnConfirm).toHaveBeenCalledWith('My Notebook');
  });

  it('should call onCancel when Escape key is pressed', () => {
    render(
      <JobNameDialog
        defaultName="My Notebook"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const input = screen.getByDisplayValue('My Notebook');
    fireEvent.keyDown(input, { key: 'Escape' });

    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('should trim whitespace from job name when confirming', () => {
    render(
      <JobNameDialog
        defaultName="  My Notebook  "
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const launchButton = screen.getByText('Launch Job');
    fireEvent.click(launchButton);

    expect(mockOnConfirm).toHaveBeenCalledWith('My Notebook');
  });
});
