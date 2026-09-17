// Toast loi (hien 6s roi tu an — quan ly boi App qua state)
export default function Toast({ message }) {
  if (!message) return null;
  return (
    <div className="toast" style={{ display: "block" }}>
      {message}
    </div>
  );
}
