import { Assignment } from '../../../model/assignment';
import * as React from 'react';
import { useFormik } from 'formik';
import {
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFnsV3';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import {
  getAssignment
} from '../../../services/assignments.service';
import { enqueueSnackbar } from 'notistack';
import { Lecture } from '../../../model/lecture';
import * as yup from 'yup';
import { SectionTitle } from '../../util/section-title';
import {
  getLateSubmissionInfo,
  ILateSubmissionInfo,
  LateSubmissionForm
} from './late-submission-form';
import { FormikValues } from 'formik/dist/types';
import moment from 'moment';
import { red } from '@mui/material/colors';
import { AllowedFilePatterns } from './allowed-files-form';
import { extractIdsFromBreadcrumbs } from '../../util/breadcrumbs';
import { getLecture } from '../../../services/lectures.service';
import { useQuery } from '@tanstack/react-query';
import { SaveAssignmentSettingsDialog } from '../../util/dialog';
import { TooltipComponent } from '../../util/tooltip';



const gradingBehaviourHelp = 
  <React.Fragment>
    Specifies the behaviour when a students submits an assignment.
    <br />
    <b>No Automatic Grading</b>: No action is taken on submit.
    <br />
    <b>Automatic Grading</b>: The assignment is being autograded as soon as the students makes a submission.
    <br />
    <b>Fully Automatic Grading</b>: The assignment is autograded and feedback is generated as soon as the student makes a submission. 
    (requires all scores to be based on autograde results)
  </React.Fragment>;

const validationSchema = yup.object({
  name: yup
    .string()
    .min(4, 'Name should be 4-50 character length')
    .max(50, 'Name should be 4-50 character length')
    .required('Name is required'),
  deadline: yup.date().nullable(),
  type: yup.mixed().oneOf(['user', 'group']),
  automatic_grading: yup.mixed().oneOf(['unassisted', 'auto', 'full_auto']),
  max_submissions: yup
    .number()
    .nullable()
    .min(1, 'Students must be able to at least submit once')
});

export const SettingsComponent = () => {
  
  const { lectureId, assignmentId } = extractIdsFromBreadcrumbs();

  const { data: lecture } = useQuery<Lecture>({
    queryKey: ['lecture', lectureId],
    queryFn: () => getLecture(lectureId),
    enabled: !!lectureId,
  });

  const { data: assignment } = useQuery<Assignment>({
    queryKey: ['assignment', assignmentId],
    queryFn: () => getAssignment(lectureId, assignmentId),
    enabled: !!lecture && !!assignmentId,
  });

  const [newAssignment, setNewAssignment] = React.useState(null)

  const [checked, setChecked] = React.useState(
    assignment.settings.deadline !== null
  );
  const [checkedLimit, setCheckedLimit] = React.useState(
    Boolean(assignment.settings.max_submissions)
  );

  const [saveDialogDisplay, setSaveDialogDisplay] = React.useState(false);

  const validateLateSubmissions = (values: FormikValues) => {
    const late_submissions: ILateSubmissionInfo[] = getLateSubmissionInfo(
      values.settings.late_submission
    );
    const error = { settings: { late_submission: { days: {}, hours: {}, scaling: {} } } };
    let nErrors = 0;

    // Validation logic for late submissions
    for (let i = 0; i < late_submissions.length; i++) {
      const info = late_submissions[i];
      if (!Number.isInteger(info.days)) {
        error.settings.late_submission.days[i] = 'Days have to be whole numbers';
        nErrors++;
      }
      if (!Number.isInteger(info.hours)) {
        error.settings.late_submission.hours[i] = 'Hours have to be whole numbers';
        nErrors++;
      }
      if (info.days < 0) {
        error.settings.late_submission.days[i] = 'Days cannot be negative';
        nErrors++;
      }
      if (info.hours < 0) {
        error.settings.late_submission.hours[i] = 'Hours cannot be negative';
        nErrors++;
      }
      if (info.scaling <= 0 || info.scaling >= 1) {
        error.settings.late_submission.scaling[i] =
          'Scaling has to be between 0 and 1 exclusive';
        nErrors++;
      }
      if (
        parseFloat(info.scaling.toFixed(3)) !== info.scaling
      ) {
        error.settings.late_submission.scaling[i] =
          'Scaling can only be specified up to 3 decimal points';
        nErrors++;
      }
      if (
        moment.duration({ days: info.days, hours: info.hours }) <=
        moment.duration(0)
      ) {
        error.settings.late_submission.days[i] = 'Period cannot be 0';
        error.settings.late_submission.hours[i] = 'Period cannot be 0';
        nErrors++;
      }
      if (i > 0) {
        const prevInfo = late_submissions[i - 1];
        if (
          moment.duration({ days: info.days, hours: info.hours }) <=
          moment.duration({ days: prevInfo.days, hours: prevInfo.hours })
        ) {
          error.settings.late_submission.days[i] = 'Periods have to be increasing';
          error.settings.late_submission.hours[i] = 'Periods have to be increasing';
          nErrors++;
        }
        if (info.scaling >= prevInfo.scaling) {
          error.settings.late_submission.scaling[i] = 'Scaling has to decrease';
          nErrors++;
        }
      }
    }

    return nErrors === 0 ? {} : error;
  };

  const formik = useFormik({
    initialValues: {
      name: assignment.name,
      settings: {
        late_submission: assignment.settings.late_submission || [],
        max_submissions: assignment.settings.max_submissions || null,
        autograde_type: assignment.settings.autograde_type,
        deadline:
          assignment.settings.deadline !== null
            ? new Date(assignment.settings.deadline)
            : null,
        allowed_files:
          assignment.settings.allowed_files === null
            ? []
            : assignment.settings.allowed_files,
      },
    },
    validationSchema: validationSchema,
    onSubmit: (values) => {
      const updatedAssignment: Assignment = {
        ...assignment,
        name: values.name,
        settings: {
          ...assignment.settings,
          ...values.settings,
          deadline: values.settings.deadline
            ? new Date(values.settings.deadline).toISOString()
            : null, // Convert Date to string or null
        },
      };
      setNewAssignment(updatedAssignment)

      setSaveDialogDisplay(true);

      
    },
    validate: validateLateSubmissions,
  });

  return (
    <Box sx={{ m: 5, flex: 1, overflow: 'auto' }}>
      <SaveAssignmentSettingsDialog lecture={lecture} assignment={newAssignment} open={saveDialogDisplay} setOpen={setSaveDialogDisplay}/>
      <SectionTitle title="Settings" />
      <form onSubmit={formik.handleSubmit}>
        <Stack spacing={2} sx={{ ml: 2, mr: 2 }}>
          <TextField
            variant="outlined"
            fullWidth
            id="name"
            name="name"
            label="Assignment Name"
            value={formik.values.name}
            onChange={formik.handleChange}
            error={formik.touched.name && Boolean(formik.errors.name)}
            helperText={formik.touched.name && formik.errors.name}
          />

          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={checked}
                  onChange={async (e) => {
                    setChecked(e.target.checked);
                    if (!e.target.checked) {
                      await formik.setFieldValue('settings.deadline', null);
                    } else {
                      await formik.setFieldValue('settings.deadline', new Date());
                    }
                  }}
                />
              }
              label="Set Deadline"
            />
            <DateTimePicker
              ampm={false}
              label="Deadline"
              disabled={!checked}
              value={formik.values.settings.deadline}
              onChange={(date: Date) => {
                formik.setFieldValue('settings.deadline', date);
                if (new Date(date).getTime() < Date.now()) {
                  enqueueSnackbar('You selected a date in the past!', {
                    variant: 'warning',
                  });
                }
              }}
            />
          </LocalizationProvider>

          <FormControlLabel
            control={
              <Checkbox
                checked={checkedLimit}
                onChange={async (e) => {
                  setCheckedLimit(e.target.checked);
                  if (!e.target.checked) {
                    await formik.setFieldValue('settings.max_submissions', null);
                  } else {
                    await formik.setFieldValue('settings.max_submissions', 1);
                  }
                }}
              />
            }
            label="Limit Number of Submissions"
          />

          <TextField
            variant="outlined"
            fullWidth
            disabled={!checkedLimit}
            type="number"
            id="max-submissions"
            name="settings.max_submissions"
            placeholder="Submissions"
            value={formik.values.settings.max_submissions || null}
            slotProps={{ htmlInput: { min: 1  } }}
            onChange={(e) => {
              formik.setFieldValue('settings.max_submissions', +e.target.value);
            }}
            helperText={
              formik.touched.settings?.max_submissions &&
              formik.errors.settings?.max_submissions
            }
            error={
              Boolean(formik.values.settings.max_submissions) &&
              formik.values.settings.max_submissions < 1
            }
          />

          <InputLabel id="auto-grading-behaviour-label">
            Auto-Grading Behaviour
            <TooltipComponent 
           
            title={gradingBehaviourHelp} 
             sx={{ ml:0.5 }}/>
          </InputLabel>
          <TextField
            select
            id="auto-grading-type-select"
            value={formik.values.settings.autograde_type}
            label="Auto-Grading Behaviour"
            placeholder="Grading"
            onChange={(e) => {
              formik.setFieldValue('settings.autograde_type', e.target.value);
            }}
          >
            <MenuItem value="auto">Automatic Grading</MenuItem>
            <MenuItem value="full_auto">Fully Automatic Grading</MenuItem>
            <MenuItem value="unassisted">No Automatic Grading</MenuItem>
          </TextField>

          <AllowedFilePatterns
            patterns={formik.values.settings.allowed_files || []}
            onChange={(updatedPatterns) =>
              formik.setFieldValue('settings.allowed_files', updatedPatterns)
            }
          />

          <Stack direction="column" spacing={2}>
            <InputLabel>
              Late Submissions
              <TooltipComponent 
                title={`Allowing late submission periods enables students to 
                        submit their assignments after the deadline, 
                        subject to a score penalty.`}
                sx={{ ml:0.5}}
                />
            </InputLabel>
            <Stack direction="column" spacing={2} sx={{ pl: 3 }}>
              {formik.values.settings.deadline !== null ? (
                <LateSubmissionForm formik={formik} />
              ) : (
                <Typography sx={{ color: red[500] }}>
                  Deadline not set! To configure late submissions, set a deadline
                  first!
                </Typography>
              )}
            </Stack>
          </Stack>
        </Stack>
        <Button
          sx={{ whiteSpace: 'nowrap', minWidth: 'auto', mt: 2 }}
          color="primary"
          variant="contained"
          type="submit"
        >
          Save changes
        </Button>
      </form>
    </Box>
  );
};
