import { Component, OnInit } from '@angular/core';

import { faQuestion } from '@fortawesome/free-solid-svg-icons';

import { SkillsService } from './skills.service'

const categories = [
    {'name': 'Undefined', 'icon': faQuestion}
];

@Component({
  selector: 'marketplace-skills',
  templateUrl: './skills.component.html',
  styleUrls: ['./skills.component.scss']
})
export class SkillsComponent implements OnInit {
    public skillCategories: Object[];
    public skills: Object;

    constructor(private skillsService: SkillsService) { }

    ngOnInit() {
        this.getAllSkills();
    }

    getAllSkills(): void {
        this.skillsService.getAllSkills().subscribe(
            (skills) => {
                this.skills = skills;
                this.get_skill_categories(skills);
            }
        )
    }

    get_skill_categories(skills): void {
        this.skillCategories = [];
        Object.keys(skills).forEach(category_name => {
            categories.forEach(category => {
                if (category.name === category_name) {
                    this.skillCategories.push(category)
                }
            })
        })
    }

    showSearchResults(searchResults): void {
        this.skills = searchResults;
        this.get_skill_categories(searchResults)
    }
}
