import type { PatientRecordData } from '../../types'

interface Props {
  patient: PatientRecordData
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ fontWeight: 600, fontSize: 14, color: '#555', marginBottom: 8 }}>{title}</div>
      {children}
    </div>
  )
}

export default function PatientRecordView({ patient }: Props) {
  return (
    <div style={{ padding: 16, background: '#fff', borderRadius: 8, border: '1px solid #e8e8e8' }}>
      <div style={{ fontWeight: 600, fontSize: 16, color: '#333', marginBottom: 16 }}>
        {'患者记录: ' + (patient.patient_name || '未知')}
      </div>

      <Section title="基本信息">
        <div style={{ fontSize: 13, color: '#666', lineHeight: 1.8 }}>
          <div>ID: {patient.patient_id}</div>
          <div>姓名: {patient.patient_name || '-'}</div>
          <div>角色: {patient.patient_role || '-'}</div>
        </div>
      </Section>

      {patient.cases.length > 0 && (
        <Section title={'病例记录 (' + patient.cases.length + ')'}>
          {patient.cases.map((c, i) => (
            <pre
              key={i}
              style={{
                background: '#fafafa',
                padding: 10,
                borderRadius: 4,
                fontSize: 12,
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                color: '#333',
                marginBottom: 8,
              }}
            >
              {JSON.stringify(c, null, 2)}
            </pre>
          ))}
        </Section>
      )}

      {patient.visits.length > 0 && (
        <Section title={'就诊记录 (' + patient.visits.length + ')'}>
          {patient.visits.map((v, i) => (
            <pre
              key={i}
              style={{
                background: '#fafafa',
                padding: 10,
                borderRadius: 4,
                fontSize: 12,
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                color: '#333',
                marginBottom: 8,
              }}
            >
              {JSON.stringify(v, null, 2)}
            </pre>
          ))}
        </Section>
      )}

      {patient.prescriptions.length > 0 && (
        <Section title={'处方记录 (' + patient.prescriptions.length + ')'}>
          {patient.prescriptions.map((p, i) => (
            <pre
              key={i}
              style={{
                background: '#fafafa',
                padding: 10,
                borderRadius: 4,
                fontSize: 12,
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                color: '#333',
                marginBottom: 8,
              }}
            >
              {JSON.stringify(p, null, 2)}
            </pre>
          ))}
        </Section>
      )}
    </div>
  )
}
