from spytest import st


def test_pnetlab_ssh_access():

    duts = ["CSR", "R2"]

    for dut in duts:

        st.banner(f"CONNECTING TO {dut}")

        output = st.show(
            dut,
            "show ip interface brief",
            skip_tmpl=True
        )

        st.log(output)

        assert output