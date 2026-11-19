import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  getStoredInterviews,
  saveStoredInterviews,
  getStoredScholarships,
  MockInterview,
} from "../mock/mockData";
import { Card, Button, Input, Badge } from "../components/ui";
import {
  Calendar,
  Clock,
  MapPin,
  AlertTriangle,
  CheckCircle2,
  Video,
  Plus,
  Trash2,
  FileText,
  AlertCircle,
} from "lucide-react";

export const InterviewsPage: React.FC = () => {
  const [interviews, setInterviews] = useState<MockInterview[]>(getStoredInterviews());
  const [scholarships] = useState(getStoredScholarships());

  // New Interview Modal/Form state
  const [showAddForm, setShowAddForm] = useState(false);
  const [newScholarshipTitle, setNewScholarshipTitle] = useState(
    scholarships[0]?.title || "Yayasan Khazanah Global Scholarship 2026"
  );
  const [newRound, setNewRound] = useState("Round 1: Screening Interview");
  const [newScheduledAt, setNewScheduledAt] = useState("2026-11-26T14:00");
  const [newDuration, setNewDuration] = useState(60);
  const [newLocation, setNewLocation] = useState("Microsoft Teams Video Call");
  const [newPrepNotes, setNewPrepNotes] = useState("Review past projects and leadership examples.");

  useEffect(() => {
    setInterviews(getStoredInterviews());
  }, []);

  // Algorithm to detect overlapping scheduled interviews
  const detectOverlaps = () => {
    const conflicts: {
      item1: MockInterview;
      item2: MockInterview;
      overlapStart: Date;
      overlapEnd: Date;
    }[] = [];

    for (let i = 0; i < interviews.length; i++) {
      for (let j = i + 1; j < interviews.length; j++) {
        const int1 = interviews[i];
        const int2 = interviews[j];

        const start1 = new Date(int1.scheduled_at).getTime();
        const end1 = start1 + int1.duration_minutes * 60 * 1000;

        const start2 = new Date(int2.scheduled_at).getTime();
        const end2 = start2 + int2.duration_minutes * 60 * 1000;

        // Overlap condition: start1 < end2 && start2 < end1
        if (start1 < end2 && start2 < end1) {
          conflicts.push({
            item1: int1,
            item2: int2,
            overlapStart: new Date(Math.max(start1, start2)),
            overlapEnd: new Date(Math.min(end1, end2)),
          });
        }
      }
    }
    return conflicts;
  };

  const conflicts = detectOverlaps();

  const handleAddInterview = (e: React.FormEvent) => {
    e.preventDefault();
    const newInt: MockInterview = {
      id: `int-${Date.now()}`,
      application_id: "app-custom",
      scholarship_title: newScholarshipTitle,
      round_name: newRound,
      scheduled_at: new Date(newScheduledAt).toISOString(),
      duration_minutes: newDuration,
      location_or_link: newLocation,
      status: "Scheduled",
      prep_notes: newPrepNotes,
    };

    const updated = [...interviews, newInt];
    setInterviews(updated);
    saveStoredInterviews(updated);
    setShowAddForm(false);
  };

  const handleDelete = (id: string) => {
    if (window.confirm("Remove this interview entry?")) {
      const updated = interviews.filter((i) => i.id !== id);
      setInterviews(updated);
      saveStoredInterviews(updated);
    }
  };

  const isItemConflicted = (item: MockInterview) => {
    return conflicts.some((c) => c.item1.id === item.id || c.item2.id === item.id);
  };

  return (
    <div className="page-interviews">
      <div className="page-header-row">
        <div>
          <h2>Interview Schedule & Preparation Hub</h2>
          <p className="page-subtitle">
            Track stage-dependent interview rounds, coordinate assessment centers, and detect scheduling collisions.
          </p>
        </div>
        <div>
          <Button onClick={() => setShowAddForm(!showAddForm)} size="sm">
            <Plus size={14} style={{ marginRight: 6 }} /> Log Scheduled Interview
          </Button>
        </div>
      </div>

      {/* Prominent Overlap Warning Alert Banner */}
      {conflicts.length > 0 ? (
        <div className="alert-banner warning-banner conflict-banner">
          <AlertTriangle size={28} className="alert-icon" />
          <div className="alert-content">
            <h4>⚠️ CRITICAL INTERVIEW TIME OVERLAP DETECTED</h4>
            <p>
              ScholarPal detected a direct timing conflict between multiple scheduled sessions!
              Please contact the sponsor coordinator to reschedule.
            </p>
            <div className="conflict-details-box">
              {conflicts.map((c, idx) => (
                <div key={idx} className="conflict-detail-row">
                  <strong>Conflict #{idx + 1}: </strong>
                  <span>
                    "{c.item1.scholarship_title}" ({c.item1.round_name}) collides with "
                    {c.item2.scholarship_title}" ({c.item2.round_name}) on{" "}
                    {c.overlapStart.toLocaleDateString("en-GB", {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                    })}!
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="alert-banner success-banner">
          <CheckCircle2 size={18} />
          <span>No scheduling overlaps detected. Your interview itinerary is clear.</span>
        </div>
      )}

      {/* Add Interview Collapsible Form */}
      {showAddForm && (
        <Card
          title="Log an Interview Assessment"
          subtitle="Record an upcoming panel or online assessment round"
          className="add-interview-card"
        >
          <form onSubmit={handleAddInterview} className="add-interview-form">
            <div className="form-row-2">
              <div className="form-group">
                <label className="form-label">Scholarship / Sponsor</label>
                <select
                  className="form-select"
                  value={newScholarshipTitle}
                  onChange={(e) => setNewScholarshipTitle(e.target.value)}
                >
                  {scholarships.map((s) => (
                    <option key={s.id} value={s.title}>
                      {s.title}
                    </option>
                  ))}
                  <option value="Bank Negara Malaysia (BNM) Kijang Scholarship">
                    Bank Negara Malaysia (BNM) Kijang Scholarship
                  </option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Interview Round / Stage Name</label>
                <Input
                  value={newRound}
                  onChange={(e) => setNewRound(e.target.value)}
                  placeholder="e.g. Assessment Center Group Case Study"
                  required
                />
              </div>
            </div>

            <div className="form-row-3">
              <div className="form-group">
                <label className="form-label">Date & Time</label>
                <Input
                  type="datetime-local"
                  value={newScheduledAt}
                  onChange={(e) => setNewScheduledAt(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Duration (Minutes)</label>
                <Input
                  type="number"
                  min="15"
                  step="15"
                  value={newDuration}
                  onChange={(e) => setNewDuration(parseInt(e.target.value) || 60)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Venue / Virtual Video Link</label>
                <Input
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  placeholder="e.g. Zoom / Menara TM KL"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Preparation Notes / Focus Areas</label>
              <Input
                value={newPrepNotes}
                onChange={(e) => setNewPrepNotes(e.target.value)}
                placeholder="Key talking points or case preparation topics"
              />
            </div>

            <div className="form-actions-right">
              <Button
                variant="secondary"
                type="button"
                onClick={() => setShowAddForm(false)}
              >
                Cancel
              </Button>
              <Button type="submit">Save to Schedule</Button>
            </div>
          </form>
        </Card>
      )}

      {/* Interviews List */}
      <div className="interviews-list-container">
        {interviews.map((item) => {
          const hasConflict = isItemConflicted(item);
          const startDate = new Date(item.scheduled_at);
          const endDate = new Date(startDate.getTime() + item.duration_minutes * 60 * 1000);

          return (
            <div
              key={item.id}
              className={`interview-item-card ${hasConflict ? "conflict-highlight" : ""}`}
            >
              <div className="interview-left-col">
                <div className="interview-date-badge">
                  <span className="month">
                    {startDate.toLocaleDateString("en-GB", { month: "short" })}
                  </span>
                  <span className="day">
                    {startDate.toLocaleDateString("en-GB", { day: "numeric" })}
                  </span>
                </div>
              </div>

              <div className="interview-center-col">
                <div className="interview-header-line">
                  <h4 className="interview-scholarship">{item.scholarship_title}</h4>
                  {hasConflict && (
                    <Badge variant="danger" className="conflict-tag">
                      <AlertCircle size={12} style={{ marginRight: 4 }} /> Overlap Conflict
                    </Badge>
                  )}
                  <Badge variant="info">{item.status}</Badge>
                </div>

                <div className="interview-round-name">{item.round_name}</div>

                <div className="interview-meta-details">
                  <div className="meta-item">
                    <Clock size={14} />
                    <span>
                      {startDate.toLocaleTimeString("en-GB", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}{" "}
                      -{" "}
                      {endDate.toLocaleTimeString("en-GB", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}{" "}
                      ({item.duration_minutes} mins)
                    </span>
                  </div>

                  <div className="meta-item">
                    <MapPin size={14} />
                    <span>{item.location_or_link}</span>
                  </div>
                </div>

                {item.prep_notes && (
                  <div className="prep-notes-box">
                    <FileText size={14} />
                    <span>
                      <strong>Prep Notes:</strong> {item.prep_notes}
                    </span>
                  </div>
                )}
              </div>

              <div className="interview-right-col">
                <button
                  type="button"
                  className="btn-icon danger"
                  onClick={() => handleDelete(item.id)}
                  title="Delete interview entry"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
