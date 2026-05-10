import streamlit as st
import pyshark
import pandas as pd
import tempfile
import asyncio

# Fix PyShark + Streamlit asyncio issue
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Streamlit page config
st.set_page_config(
    page_title="Wireshark Packet Analyzer",
    layout="wide"
)

# Title
st.title("🛡️ Wireshark Packet Analyzer")
st.markdown("Analyze HTTP, DNS, and TLS packets from PCAP files.")

# Sidebar
st.sidebar.header("Project Information")
st.sidebar.info(
    """
    This project analyzes:
    - HTTP packets
    - DNS queries
    - TLS handshakes
    
    Upload a .pcap or .pcapng file to begin analysis.
    """
)

# File uploader
uploaded_file = st.file_uploader(
    "📂 Upload PCAP File",
    type=["pcap", "pcapng"]
)

# Analyze uploaded file
if uploaded_file is not None:

    st.success("File uploaded successfully!")

    # Save uploaded file temporarily
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_file.read())

    st.info("Reading packets... Please wait.")

    packet_data = []

    try:
        # Read packets
        capture = pyshark.FileCapture(temp_file.name)

        for packet in capture:

            protocol = packet.highest_layer

            # Safe IP extraction
            src = "N/A"
            dst = "N/A"

            if hasattr(packet, "ip"):
                src = packet.ip.src
                dst = packet.ip.dst

            length = packet.length

            info = ""

            # Protocol identification
            if protocol == "HTTP":
                info = "HTTP Request/Response"

            elif protocol == "DNS":
                info = "DNS Query/Response"

            elif protocol == "TLS":
                info = "TLS Handshake/Application Data"

            packet_data.append({
                "Protocol": protocol,
                "Source IP": src,
                "Destination IP": dst,
                "Packet Length": length,
                "Info": info
            })

        capture.close()

        # Create dataframe
        df = pd.DataFrame(packet_data)

        if not df.empty:

            # Packet table
            st.subheader("📊 Packet Analysis")

            st.dataframe(
                df,
                use_container_width=True
            )

            # Statistics
            st.subheader("📈 Protocol Statistics")

            protocol_counts = df["Protocol"].value_counts()

            st.bar_chart(protocol_counts)

            # Metrics
            st.subheader("📌 Summary")

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Packets", len(df))
            col2.metric("Protocols Found", df["Protocol"].nunique())
            col3.metric("HTTP Packets", (df["Protocol"] == "HTTP").sum())

            # DNS packets
            dns_count = (df["Protocol"] == "DNS").sum()

            # TLS packets
            tls_count = (df["Protocol"] == "TLS").sum()

            st.write(f"### DNS Packets: {dns_count}")
            st.write(f"### TLS Packets: {tls_count}")

            # Download CSV
            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇ Download Analysis Report (CSV)",
                data=csv,
                file_name="packet_analysis_report.csv",
                mime="text/csv"
            )

            st.success("✅ Analysis Completed Successfully!")

        else:
            st.warning("No packets found in uploaded file.")

    except Exception as e:
        st.error(f"❌ Error while analyzing packets: {e}")

# Footer
st.markdown("---")
st.markdown(
    "### 👨‍💻 Developed for Cybersecurity Packet Analysis Project"
)