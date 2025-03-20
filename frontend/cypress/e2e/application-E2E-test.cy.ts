describe("Test Application", () => {
  it("should go through a whole Application check", () => {
    const wait = true;

    function checkAndAct() {
      cy.url().then((currentUrl) => {
        if (currentUrl.includes("ticket")) {
          cy.log("Ticket page detected, stopping execution.");
          return;
        }

        cy.get("body").then(($body) => {
          if ($body.find("button#btn-ticket").length > 0) {
            cy.get("button#btn-ticket").then(($btn) => {
              if ($btn.is(":visible")) {
                cy.wrap($btn).click();
                return;
              }
            });
          } else {
            cy.get('input[name="input"]').then(($input) => {
              if (!$input.is(":disabled")) {
                cy.get("body").then(($body) => {
                  if (
                    $body.find('div:contains("Please create a Ticket.")')
                      .length === 0
                  ) {
                    cy.wrap($input).type("None of these helped.{enter}");
                  } else {
                    cy.wrap($input).type(
                      "Monitor: BENQ Senseye 3, Laptop: Lenovo Yoga 370, OS: Windows 10, Connection: HDMI, Issue started yesterday morning. Monitor works with other PCs.{enter}"
                    );
                  }
                });
              }
            });
          }
        });

        cy.wait(1000);
        checkAndAct();
      });
    }

    cy.visit("/login");
    cy.pause();
    cy.contains("AI Chat").click();
    cy.get('input[name="input"]').type("My monitor does not work.{enter}");
    checkAndAct();
    wait && cy.wait(1000);
    cy.get(".btn-assign").click();
    wait && cy.wait(1000);
    cy.contains(".assignee-dropdown", "Technician Bar").click();
    wait && cy.wait(1000);
    cy.get(".btn-assign").click();
    wait && cy.wait(1000);
    cy.get(".assignee-dropdown")
      .contains("Unassigned", { timeout: 5000 })
      .click();
    wait && cy.wait(1000);
    cy.contains("Close Ticket").click();
    wait && cy.wait(1000);
    cy.contains("Reopen Ticket").click();
    wait && cy.wait(1000);
    cy.get('input[name="input"]').type("Test Message{enter}");
    wait && cy.wait(1000);
    cy.contains("My Tickets").click();
    cy.contains("Ticket ID").should("exist");
    wait && cy.wait(1000);
    cy.contains("Technician Portal").click();
    cy.contains("Ticket ID").should("exist");
    wait && cy.wait(1000);
    cy.contains("Logout").click();
  });
});
