import { Component, OnInit } from '@angular/core';

import { SkillsService, AvailableSkill } from '../skills.service';
import { InstallService } from '../install.service';

@Component({
    selector: 'market-skill-summary',
    templateUrl: './skill-summary.component.html',
    styleUrls: ['./skill-summary.component.scss'],
})
export class SkillSummaryComponent implements OnInit {
    public skillCategories: string[];
    public availableSkills: AvailableSkill[];


    constructor(
        private installService: InstallService,
        private skillsService: SkillsService,
    ) { }

    ngOnInit() {
        this.getAvailableSkills();
    }

    /** Issue and API call to retrieve all the available skills. */
    getAvailableSkills(): void {
        this.skillsService.getAvailableSkills().subscribe(
            (skills) => {
                this.availableSkills = skills;
                this.skillCategories = this.skillsService.getSkillCategories();
                this.installService.getSkillInstallations();
            }
        );
    }

    /** Skills are displayed by category; this function will do the filtering */
    filterSkillsByCategory(category: string): AvailableSkill[] {
        return this.availableSkills.filter(
            (skill) => skill.marketCategory === category
        );
    }

    /** Change the view to display only those matching the search criteria. */
    showSearchResults(searchResults): void {
        this.availableSkills = searchResults;
        this.skillCategories = this.skillsService.getSkillCategories();
    }

}
